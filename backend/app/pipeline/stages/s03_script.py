"""
阶段3：逐场景剧本
"""

import json
from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.stage import Stage
from app.models.candidate import Candidate
from app.schemas.enums import StageType
from app.pipeline.stages.base import BaseStage
from app.pipeline.json_schemas import SCRIPT_SCHEMA
from app.pipeline.prompts import SCRIPT_TEMPLATE, SCRIPT_EXAMPLE

if TYPE_CHECKING:
    from app.suppliers.registry import SupplierRegistry


class ScriptStage(BaseStage):
    stage_type = StageType.SCRIPT

    def build_prompt(self, project: Project, previous_contents: dict[str, Any]) -> str:
        outline = previous_contents
        episodes_json = json.dumps(outline.get("episodes", []), indent=2, ensure_ascii=False)
        episode_count = len(outline.get("episodes", []))
        return SCRIPT_TEMPLATE.format(
            world_bible=previous_contents.get("world_bible_summary", ""),
            characters_json=json.dumps(previous_contents.get("characters", []), indent=2, ensure_ascii=False),
            current_episode=episodes_json,
            episode_count=episode_count,
            schema=json.dumps(SCRIPT_SCHEMA, indent=2, ensure_ascii=False),
            example=SCRIPT_EXAMPLE,
        )

    def validate_content(self, content: dict[str, Any]) -> tuple[bool, str | None]:
        from jsonschema import validate, ValidationError as JsonSchemaError
        try:
            validate(instance=content, schema=SCRIPT_SCHEMA)
            return True, None
        except JsonSchemaError as e:
            return False, f"JSON Schema 校验失败: {e.message}"

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
                    "stage_type": StageType.SCRIPT.value,
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
                schema=SCRIPT_SCHEMA,
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
                        "stage_type": StageType.SCRIPT.value,
                        "progress_current": i + 1,
                        "progress_total": num_candidates,
                        "status": "generating",
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

        await db.flush()
        return candidates