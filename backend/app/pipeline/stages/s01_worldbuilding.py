"""
阶段1：世界观与角色
使用 LLM 生成 JSON，用 jsonschema 校验。
集成角色状态管理功能。
"""

import json
from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.stage import Stage
from app.models.candidate import Candidate
from app.models.continuity import CharacterState
from app.schemas.enums import StageType
from app.pipeline.stages.base import BaseStage
from app.pipeline.json_schemas import WORLDBUILDING_SCHEMA
from app.pipeline.prompts import WORLDBUILDING_TEMPLATE, WORLDBUILDING_EXAMPLE

if TYPE_CHECKING:
    from app.suppliers.registry import SupplierRegistry


class WorldbuildingStage(BaseStage):
    stage_type = StageType.WORLDBUILDING

    def build_prompt(self, project: Project, previous_contents: dict[str, Any]) -> str:
        return WORLDBUILDING_TEMPLATE.format(
            genre=project.genre,
            description=project.description,
            target_episodes=project.target_episodes,
            schema=json.dumps(WORLDBUILDING_SCHEMA, indent=2, ensure_ascii=False),
            example=WORLDBUILDING_EXAMPLE,
        )

    def validate_content(self, content: dict[str, Any]) -> tuple[bool, str | None]:
        from jsonschema import validate, ValidationError as JsonSchemaError
        try:
            validate(instance=content, schema=WORLDBUILDING_SCHEMA)
            return True, None
        except JsonSchemaError as e:
            return False, f"JSON Schema 校验失败: {e.message}"

    async def extract_and_save_character_states(
        self,
        db: AsyncSession,
        project: Project,
        content: dict[str, Any],
        candidate_id: str,
    ) -> None:
        """
        从生成的内容中提取角色信息并保存到CharacterState表中
        
        Args:
            db: 数据库会话
            project: 项目对象
            content: 生成的世界观内容
            candidate_id: 候选ID
        """
        characters = content.get("characters", [])
        for char in characters:
            char_name = char.get("name", "")
            if not char_name:
                continue
            
            # 检查是否已存在该角色的状态记录
            from sqlalchemy import select
            existing = await db.execute(
                select(CharacterState).where(
                    CharacterState.project_id == project.id,
                    CharacterState.character_name == char_name,
                )
            )
            existing_state = existing.scalar_one_or_none()
            
            if existing_state:
                # 更新现有记录
                existing_state.outfit_description = char.get("appearance", "")
                existing_state.hairstyle = char.get("hairstyle", "")
                existing_state.age_appearance = char.get("age", "")
                existing_state.accessories = char.get("accessories", {})
                existing_state.notes = f"从候选 {candidate_id} 更新"
            else:
                # 创建新的角色状态记录
                character_state = CharacterState(
                    project_id=project.id,
                    character_name=char_name,
                    episode_start=1,
                    episode_end=project.target_episodes,
                    outfit_description=char.get("appearance", ""),
                    hairstyle=char.get("hairstyle", ""),
                    age_appearance=char.get("age", ""),
                    accessories=char.get("accessories", {}),
                    signature_items=char.get("signature_items", {}),
                    notes=f"从候选 {candidate_id} 创建",
                )
                db.add(character_state)

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
                    "stage_type": StageType.WORLDBUILDING.value,
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
                schema=WORLDBUILDING_SCHEMA,
            )
            candidate = Candidate(
                stage_id=stage.id,
                content=content,
                metadata_={"candidate_index": i},
            )
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
                        "stage_type": StageType.WORLDBUILDING.value,
                        "progress_current": i + 1,
                        "progress_total": num_candidates,
                        "status": "generating",
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

        await db.flush()
        return candidates