"""
阶段1：世界观与角色
使用 LLM 生成 JSON，用 jsonschema 校验。
"""

import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.stage import Stage
from app.models.candidate import Candidate
from app.schemas.enums import StageType
from app.pipeline.stages.base import BaseStage
from app.pipeline.json_schemas import WORLDBUILDING_SCHEMA
from app.pipeline.prompts import WORLDBUILDING_TEMPLATE, WORLDBUILDING_EXAMPLE


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

        candidates: list[Candidate] = []
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

        await db.flush()
        return candidates
