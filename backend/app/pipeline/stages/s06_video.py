"""
阶段6：视频片段
从阶段4的 shots + 阶段5的关键帧，调用视频供应商。
"""

import uuid
from typing import Any
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.stage import Stage
from app.models.candidate import Candidate, Artifact
from app.schemas.enums import StageType, SupplierCapability, FileType
from app.pipeline.stages.base import BaseStage
from app.config import settings


class VideoStage(BaseStage):
    stage_type = StageType.VIDEO

    def build_prompt(self, project: Project, previous_contents: dict[str, Any]) -> str:
        return "Video generation uses video prompts from storyboard stage directly."

    def validate_content(self, content: dict[str, Any]) -> tuple[bool, str | None]:
        clips = content.get("generated_clips", [])
        if not clips:
            return False, "No generated clips in content"
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
        # 获取阶段4 shots
        sb_stage_result = await db.execute(
            select(Stage).where(
                Stage.project_id == project.id,
                Stage.stage_type == StageType.STORYBOARD.value,
            )
        )
        sb_stage = sb_stage_result.scalar_one()
        sb_candidate_result = await db.execute(
            select(Candidate).where(Candidate.id == sb_stage.current_candidate_id)
        )
        sb_candidate = sb_candidate_result.scalar_one()
        shots = sb_candidate.content.get("shots", [])

        # 获取阶段5关键帧
        kf_stage_result = await db.execute(
            select(Stage).where(
                Stage.project_id == project.id,
                Stage.stage_type == StageType.KEYFRAME.value,
            )
        )
        kf_stage = kf_stage_result.scalar_one()
        kf_candidate_result = await db.execute(
            select(Candidate).where(Candidate.id == kf_stage.current_candidate_id)
        )
        kf_candidate = kf_candidate_result.scalar_one()
        kf_images = {img["shot_ref"]: img for img in kf_candidate.content.get("generated_images", [])}

        video_supplier = await registry.get_with_fallback(SupplierCapability.VIDEO)

        candidates: list[Candidate] = []
        for cand_idx in range(num_candidates):
            generated_clips: list[dict[str, Any]] = []
            project_dir = Path(settings.data_dir) / "projects" / str(project.id)
            project_dir.mkdir(parents=True, exist_ok=True)

            for shot in shots:
                shot_num = shot["shot_number"]
                ref_image_data = kf_images.get(shot_num)

                ref_image_bytes: bytes | None = None
                if ref_image_data:
                    ref_artifact_result = await db.execute(
                        select(Artifact).where(Artifact.id == ref_image_data["artifact_id"])
                    )
                    ref_artifact = ref_artifact_result.scalar_one_or_none()
                    if ref_artifact:
                        ref_path = Path(settings.data_dir) / ref_artifact.file_path
                        if ref_path.exists():
                            ref_image_bytes = ref_path.read_bytes()

                video_bytes = await video_supplier.generate_video(
                    prompt=shot["video_prompt"],
                    reference_image=ref_image_bytes,
                    duration_seconds=shot.get("duration_sec", 5.0),
                )

                file_name = f"video_s{shot_num}_c{cand_idx}.mp4"
                file_path = project_dir / file_name
                file_path.write_bytes(video_bytes)

                artifact = Artifact(
                    candidate_id=uuid.uuid4(),
                    file_type=FileType.VIDEO.value,
                    file_path=str(file_path.relative_to(Path(settings.data_dir))),
                    file_size=len(video_bytes),
                    mime_type="video/mp4",
                    metadata_={"shot_number": shot_num},
                )
                db.add(artifact)
                await db.flush()

                generated_clips.append({
                    "shot_ref": shot_num,
                    "prompt_used": shot["video_prompt"],
                    "reference_image_id": ref_image_data.get("artifact_id") if ref_image_data else None,
                    "duration_sec": shot.get("duration_sec", 5.0),
                    "resolution": config.get("resolution", "1280x720"),
                    "artifact_id": str(artifact.id),
                })

            candidate = Candidate(
                stage_id=stage.id,
                content={"generated_clips": generated_clips},
                metadata_={"candidate_index": cand_idx},
            )
            db.add(candidate)
            await db.flush()

            # 关联 artifacts 到 candidate
            for clip_data in generated_clips:
                art_result = await db.execute(
                    select(Artifact).where(Artifact.id == clip_data["artifact_id"])
                )
                art = art_result.scalar_one_or_none()
                if art:
                    art.candidate_id = candidate.id

            candidates.append(candidate)

        await db.flush()
        return candidates
