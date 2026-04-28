"""
阶段4：分镜与提示词
集成场景资产管理功能。
"""

import json
from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.stage import Stage
from app.models.candidate import Candidate
from app.models.continuity import SceneAsset
from app.schemas.enums import StageType
from app.pipeline.stages.base import BaseStage
from app.pipeline.json_schemas import STORYBOARD_SCHEMA
from app.pipeline.prompts import STORYBOARD_TEMPLATE, STORYBOARD_EXAMPLE

if TYPE_CHECKING:
    from app.suppliers.registry import SupplierRegistry


class StoryboardStage(BaseStage):
    stage_type = StageType.STORYBOARD

    def build_prompt(self, project: Project, previous_contents: dict[str, Any]) -> str:
        scenes = previous_contents.get("scenes", [])
        characters = previous_contents.get("characters", [])
        appearances = "\n".join(
            f"- {c['name']}: {c.get('appearance', '')}" for c in characters
        )
        return STORYBOARD_TEMPLATE.format(
            world_bible=previous_contents.get("world_bible", ""),
            character_appearances=appearances,
            scenes_json=json.dumps(scenes, indent=2, ensure_ascii=False),
            schema=json.dumps(STORYBOARD_SCHEMA, indent=2, ensure_ascii=False),
            example=STORYBOARD_EXAMPLE,
        )

    def validate_content(self, content: dict[str, Any]) -> tuple[bool, str | None]:
        from jsonschema import validate, ValidationError as JsonSchemaError
        try:
            validate(instance=content, schema=STORYBOARD_SCHEMA)
            return True, None
        except JsonSchemaError as e:
            return False, f"JSON Schema 校验失败: {e.message}"

    async def extract_and_save_scene_assets(
        self,
        db: AsyncSession,
        project: Project,
        content: dict[str, Any],
        candidate_id: str,
    ) -> None:
        """
        从生成的内容中提取场景信息并保存到SceneAsset表中
        
        Args:
            db: 数据库会话
            project: 项目对象
            content: 生成的分镜内容
            candidate_id: 候选ID
        """
        scenes = content.get("scenes", [])
        for scene in scenes:
            scene_name = scene.get("name", "")
            if not scene_name:
                continue
            
            # 检查是否已存在该场景的资产记录
            from sqlalchemy import select
            existing = await db.execute(
                select(SceneAsset).where(
                    SceneAsset.project_id == project.id,
                    SceneAsset.scene_name == scene_name,
                )
            )
            existing_asset = existing.scalar_one_or_none()
            
            if existing_asset:
                # 更新现有记录
                existing_asset.description = scene.get("description", "")
                existing_asset.layout_description = scene.get("layout", "")
                existing_asset.notes = f"从候选 {candidate_id} 更新"
            else:
                # 创建新的场景资产记录
                scene_asset = SceneAsset(
                    project_id=project.id,
                    scene_name=scene_name,
                    scene_type=scene.get("type", "interior"),
                    description=scene.get("description", ""),
                    layout_description=scene.get("layout", ""),
                    notes=f"从候选 {candidate_id} 创建",
                )
                db.add(scene_asset)

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
                    "stage_type": StageType.STORYBOARD.value,
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
                schema=STORYBOARD_SCHEMA,
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
                        "stage_type": StageType.STORYBOARD.value,
                        "progress_current": i + 1,
                        "progress_total": num_candidates,
                        "status": "generating",
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

        await db.flush()
        return candidates