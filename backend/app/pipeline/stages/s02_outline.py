"""
阶段2：剧情大纲
集成节奏模板功能。
"""

import json
from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.stage import Stage
from app.models.candidate import Candidate
from app.models.continuity import PacingTemplate
from app.schemas.enums import StageType
from app.pipeline.stages.base import BaseStage
from app.pipeline.json_schemas import OUTLINE_SCHEMA
from app.pipeline.prompts import OUTLINE_TEMPLATE, OUTLINE_EXAMPLE

if TYPE_CHECKING:
    from app.suppliers.registry import SupplierRegistry


class OutlineStage(BaseStage):
    stage_type = StageType.OUTLINE

    def build_prompt(self, project: Project, previous_contents: dict[str, Any]) -> str:
        # 获取项目对应的节奏模板
        pacing_template = self._get_pacing_template(project)
        
        base_prompt = OUTLINE_TEMPLATE.format(
            world_bible=previous_contents.get("world_bible", ""),
            characters_json=json.dumps(previous_contents.get("characters", []), indent=2, ensure_ascii=False),
            target_episodes=project.target_episodes,
            schema=json.dumps(OUTLINE_SCHEMA, indent=2, ensure_ascii=False),
            example=OUTLINE_EXAMPLE,
        )
        
        # 如果有节奏模板，添加节奏指导
        if pacing_template:
            pacing_guidance = f"\n\n节奏指导：\n{json.dumps(pacing_template, indent=2, ensure_ascii=False)}"
            base_prompt += pacing_guidance
            
        return base_prompt

    def _get_pacing_template(self, project: Project) -> dict[str, Any] | None:
        """
        获取项目对应的节奏模板
        
        Args:
            project: 项目对象
            
        Returns:
            节奏模板结构，如果没有找到则返回None
        """
        # 这里可以根据项目类型、流派等选择合适的节奏模板
        # 目前简化处理，返回一个默认的节奏结构
        return {
            "hook_3sec": "前3秒必须有强烈的视觉冲击或悬念",
            "cliffhanger": "每集结尾必须留下悬念",
            "pacing": "快节奏，每1-2分钟一个小高潮",
            "target_duration_sec": project.target_duration_minutes * 60
        }

    def validate_content(self, content: dict[str, Any]) -> tuple[bool, str | None]:
        from jsonschema import validate, ValidationError as JsonSchemaError
        try:
            validate(instance=content, schema=OUTLINE_SCHEMA)
            return True, None
        except JsonSchemaError as e:
            return False, f"JSON Schema 校验失败: {e.message}"

    async def extract_and_save_pacing_template(
        self,
        db: AsyncSession,
        project: Project,
        content: dict[str, Any],
        candidate_id: str,
    ) -> None:
        """
        从生成的内容中提取节奏信息并保存到PacingTemplate表中
        
        Args:
            db: 数据库会话
            project: 项目对象
            content: 生成的剧情大纲内容
            candidate_id: 候选ID
        """
        # 检查是否已存在该项目的节奏模板记录
        from sqlalchemy import select
        existing = await db.execute(
            select(PacingTemplate).where(
                PacingTemplate.name == f"project_{project.id}_pacing"
            )
        )
        existing_template = existing.scalar_one_or_none()
        
        # 构建节奏结构
        pacing_structure = {
            "genre": project.genre,
            "target_episodes": project.target_episodes,
            "target_duration_sec": project.target_duration_minutes * 60,
            "scenes": content.get("scenes", []),
            "pacing_notes": content.get("pacing_notes", ""),
        }
        
        if existing_template:
            # 更新现有记录
            existing_template.structure = pacing_structure
            existing_template.genre = project.genre
            existing_template.usage_count += 1
            existing_template.description = f"从候选 {candidate_id} 更新"
        else:
            # 创建新的节奏模板记录
            pacing_template = PacingTemplate(
                name=f"project_{project.id}_pacing",
                description=f"项目 {project.name} 的节奏模板",
                genre=project.genre,
                structure=pacing_structure,
                target_duration_sec=project.target_duration_minutes * 60,
                usage_count=1,
            )
            db.add(pacing_template)

    async def generate(
        self,
        db: AsyncSession,
        stage: Stage,
        project: Project,
        prompt: str,
        config: dict[str, Any],
        num_candidates: int,
        registry: "SupplierRegistry",
    ) -> list[Candidate]:
        from app.services.generation_service import call_llm_for_json
        from app.ws.hub import ws_hub
        from datetime import datetime, timezone

        candidates: list[Candidate] = []
        
        # 初始化进度
        stage.progress_total = num_candidates
        stage.progress_current = 0
        await db.flush()

        # 发送初始进度
        await ws_hub.broadcast_to_project(
            str(project.id),
            {
                "type": "stage_progress",
                "data": {
                    "project_id": str(project.id),
                    "stage_type": StageType.OUTLINE.value,
                    "progress_current": 0,
                    "progress_total": num_candidates,
                    "status": "generating",
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        for i in range(num_candidates):
            content = await call_llm_for_json(
                registry=registry,
                system_prompt=prompt,
                user_prompt=f"请生成第 {i + 1} 个候选方案。",
                schema=OUTLINE_SCHEMA,
            )
            candidate = Candidate(stage_id=stage.id, content=content, metadata_={"candidate_index": i})
            db.add(candidate)
            candidates.append(candidate)

            # 更新进度
            stage.progress_current = i + 1
            await db.flush()
            
            # 发送进度更新
            await ws_hub.broadcast_to_project(
                str(project.id),
                {
                    "type": "stage_progress",
                    "data": {
                        "project_id": str(project.id),
                        "stage_type": StageType.OUTLINE.value,
                        "progress_current": i + 1,
                        "progress_total": num_candidates,
                        "status": "generating",
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

        await db.flush()
        return candidates