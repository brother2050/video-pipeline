"""
阶段5：关键帧图像
不使用 LLM。直接从阶段4的 shots 提取 image_prompt，调用图像供应商。
"""

import uuid
from typing import TYPE_CHECKING, Any
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.stage import Stage
from app.models.candidate import Candidate, Artifact
from app.schemas.enums import StageType, SupplierCapability, FileType
from app.pipeline.stages.base import BaseStage
from app.config import settings

if TYPE_CHECKING:
    from app.suppliers.registry import SupplierRegistry


class KeyframeStage(BaseStage):
    stage_type = StageType.KEYFRAME

    def build_prompt(self, project: Project, previous_contents: dict[str, Any]) -> str:
        return "Keyframe generation uses image prompts from storyboard stage directly."

    def validate_content(self, content: dict[str, Any]) -> tuple[bool, str | None]:
        images = content.get("generated_images", [])
        if not images:
            return False, "No generated images in content"
        return True, None

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
        # 1. 获取阶段4的已锁定候选
        storyboard_stage_result = await db.execute(
            select(Stage).where(
                Stage.project_id == project.id,
                Stage.stage_type == StageType.STORYBOARD.value,
            )
        )
        sb_stage = storyboard_stage_result.scalar_one_or_none()
        if sb_stage is None or sb_stage.current_candidate_id is None:
            from app.exceptions import PipelineError
            raise PipelineError("Storyboard stage not completed")

        sb_candidate_result = await db.execute(
            select(Candidate).where(Candidate.id == sb_stage.current_candidate_id)
        )
        sb = sb_candidate_result.scalar_one()
        shots = sb.content.get("shots", [])

        # 2. 对每个 shot 生成图片
        image_supplier = await registry.get_with_fallback(SupplierCapability.IMAGE)

        candidates: list[Candidate] = []
        for cand_idx in range(num_candidates):
            generated_images: list[dict[str, Any]] = []
            
            # 先创建 Candidate 对象
            candidate = Candidate(
                stage_id=stage.id,
                content={"generated_images": []},
                metadata_={"candidate_index": cand_idx},
            )
            db.add(candidate)
            await db.flush()
            
            project_dir = Path(settings.data_dir) / "projects" / str(project.id)
            project_dir.mkdir(parents=True, exist_ok=True)

            for shot in shots:
                img_bytes_list = await image_supplier.generate_image(
                    prompt=shot["image_prompt"],
                    negative_prompt=shot.get("negative_prompt", ""),
                    width=config.get("width", 1536),
                    height=config.get("height", 864),
                    num_images=1,
                )
                if img_bytes_list:
                    img_bytes = img_bytes_list[0]
                    file_name = f"keyframe_s{shot['shot_number']}_c{cand_idx}.png"
                    file_path = project_dir / file_name
                    file_path.write_bytes(img_bytes)

                    artifact = Artifact(
                        candidate_id=candidate.id,
                        file_type=FileType.IMAGE.value,
                        file_path=str(file_path.relative_to(Path(settings.data_dir))),
                        file_size=len(img_bytes),
                        mime_type="image/png",
                        metadata_={"shot_number": shot["shot_number"]},
                    )
                    db.add(artifact)
                    await db.flush()

                    generated_images.append({
                        "shot_ref": shot["shot_number"],
                        "prompt_used": shot["image_prompt"],
                        "negative_prompt_used": shot.get("negative_prompt", ""),
                        "width": config.get("width", 1536),
                        "height": config.get("height", 864),
                        "artifact_id": str(artifact.id),
                    })

            # 更新 candidate 的 content
            candidate.content = {"generated_images": generated_images}
            await db.flush()

            candidates.append(candidate)

        await db.commit()
        return candidates