"""
阶段9：精剪出片
读取阶段8粗剪视频，应用效果后输出最终成片。
"""

import uuid
from typing import TYPE_CHECKING, Any, cast
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
    from app.suppliers.base import PostBaseSupplier


class FinalCutStage(BaseStage):
    stage_type = StageType.FINAL_CUT

    def build_prompt(self, project: Project, previous_contents: dict[str, Any]) -> str:
        return "Final cut applies post-processing effects to the rough cut video."

    def validate_content(self, content: dict[str, Any]) -> tuple[bool, str | None]:
        if "output_artifact_id" not in content:
            return False, "Missing output_artifact_id"
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
        from app.ws.hub import ws_hub
        from datetime import datetime, timezone

        # 获取阶段8粗剪视频
        rc_stage_result = await db.execute(
            select(Stage).where(
                Stage.project_id == project.id,
                Stage.stage_type == StageType.ROUGH_CUT.value,
            )
        )
        rc_stage = rc_stage_result.scalar_one()
        rc_candidate_result = await db.execute(
            select(Candidate).where(Candidate.id == rc_stage.current_candidate_id)
        )
        rc_candidate = rc_candidate_result.scalar_one()
        rc_content = rc_candidate.content
        rough_cut_artifact_id = rc_content.get("output_artifact_id", "")

        rough_cut_artifact_result = await db.execute(
            select(Artifact).where(Artifact.id == rough_cut_artifact_id)
        )
        rough_cut_artifact = rough_cut_artifact_result.scalar_one()
        rough_cut_path = str(Path(settings.data_dir) / rough_cut_artifact.file_path)

        # 获取阶段3剧本用于字幕
        script_stage_result = await db.execute(
            select(Stage).where(
                Stage.project_id == project.id,
                Stage.stage_type == StageType.SCRIPT.value,
            )
        )
        script_stage = script_stage_result.scalar_one()
        script_candidate_result = await db.execute(
            select(Candidate).where(Candidate.id == script_stage.current_candidate_id)
        )
        script_candidate = script_candidate_result.scalar_one()
        scenes = script_candidate.content.get("scenes", [])

        from app.suppliers.base import PostBaseSupplier
        ffmpeg_supplier = cast(PostBaseSupplier, await registry.get_with_fallback(SupplierCapability.POST))
        project_dir = Path(settings.data_dir) / "projects" / str(project.id)

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
                    "stage_type": StageType.FINAL_CUT.value,
                    "progress_current": 0,
                    "progress_total": num_candidates,
                    "status": "generating",
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        candidates: list[Candidate] = []
        for cand_idx in range(num_candidates):
            # 生成 SRT 字幕文件
            srt_path = project_dir / f"subtitles_{cand_idx}.srt"
            self._generate_srt(scenes, srt_path)

            effects = config.get("effects", [
                {"type": "color_grade", "params": {"lut": "cinematic_cold", "intensity": 0.8}},
                {"type": "subtitle", "params": {"font": "Noto Sans SC", "size": 48, "position": "bottom_center"}},
                {"type": "vignette", "params": {"intensity": 0.3}},
                {"type": "grain", "params": {"intensity": 0.05}},
            ])

            output_name = f"final_cut_{cand_idx}.mp4"
            output_path = project_dir / output_name

            result_path = await ffmpeg_supplier.process(
                input_files=[rough_cut_path, str(srt_path)],
                output_path=str(output_path),
                params={
                    "operation": "final_cut",
                    "effects": effects,
                    "resolution": config.get("resolution", "1920x1080"),
                    "fps": config.get("fps", 24),
                    "bitrate": config.get("bitrate", "8M"),
                    "audio_codec": config.get("audio_codec", "aac"),
                    "audio_bitrate": config.get("audio_bitrate", "192k"),
                },
            )

            output_stat = Path(result_path).stat()
            artifact = Artifact(
                candidate_id=uuid.uuid4(),
                file_type=FileType.VIDEO.value,
                file_path=str(Path(result_path).relative_to(Path(settings.data_dir))),
                file_size=output_stat.st_size,
                mime_type="video/mp4",
                metadata_={"operation": "final_cut"},
            )
            db.add(artifact)
            await db.flush()

            candidate = Candidate(
                stage_id=stage.id,
                content={
                    "effects": effects,
                    "output_format": "mp4",
                    "resolution": config.get("resolution", "1920x1080"),
                    "fps": config.get("fps", 24),
                    "bitrate": config.get("bitrate", "8M"),
                    "output_artifact_id": str(artifact.id),
                },
                metadata_={"candidate_index": cand_idx},
            )
            db.add(candidate)
            await db.flush()

            artifact.candidate_id = candidate.id
            candidates.append(candidate)

            # 更新进度
            stage.progress_current = cand_idx + 1
            await db.flush()
            
            # 发送进度更新
            await ws_hub.broadcast_to_project(
                str(project.id),
                {
                    "type": "stage_progress",
                    "data": {
                        "project_id": str(project.id),
                        "stage_type": StageType.FINAL_CUT.value,
                        "progress_current": cand_idx + 1,
                        "progress_total": num_candidates,
                        "status": "generating",
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

        await db.flush()
        return candidates

    def _generate_srt(self, scenes: list[dict[str, Any]], srt_path: Path) -> None:
        """从剧本场景生成 SRT 字幕文件"""
        lines: list[str] = []
        counter = 1
        for scene in scenes:
            for dlg in scene.get("dialogue", []):
                character = dlg.get("character", "")
                line = dlg.get("line", "")
                lines.append(str(counter))
                lines.append(f"00:00:{counter * 3:02d},000 --> 00:00:{(counter + 1) * 3:02d},000")
                lines.append(f"{character}: {line}")
                lines.append("")
                counter += 1
        srt_path.write_text("\n".join(lines), encoding="utf-8")