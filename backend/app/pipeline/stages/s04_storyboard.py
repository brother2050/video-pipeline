"""
阶段4：分镜与提示词
"""

import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.stage import Stage
from app.models.candidate import Candidate
from app.schemas.enums import StageType
from app.pipeline.stages.base import BaseStage
from app.pipeline.json_schemas import STORYBOARD_SCHEMA
from app.pipeline.prompts import STORYBOARD_TEMPLATE, STORYBOARD_EXAMPLE


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
                schema=STORYBOARD_SCHEMA,
            )
            candidate = Candidate(stage_id=stage.id, content=content, metadata_={"candidate_index": i})
            db.add(candidate)
            candidates.append(candidate)
        await db.flush()
        return candidates
