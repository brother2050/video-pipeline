"""
阶段8：粗剪合成
读取阶段6视频 + 阶段7音频，用 FFmpeg 合成。
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


class RoughCutStage(BaseStage):
    stage_type = StageType.ROUGH_CUT

    def build_prompt(self, project: Project, previous_contents: dict[str, Any]) -> str:
        return "Rough cut uses FFmpeg to merge video and audio tracks."

    def validate_content(self, content: dict[str, Any]) -> tuple[bool, str | None]:
        timeline = content.get("timeline", [])
        if not timeline:
            return False, "No timeline in content"
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

        # 获取阶段6视频
        video_stage_result = await db.execute(
            select(Stage).where(
                Stage.project_id == project.id,
                Stage.stage_type == StageType.VIDEO.value,
            )
        )
        video_stage = video_stage_result.scalar_one()
        video_candidate_result = await db.execute(
            select(Candidate).where(Candidate.id == video_stage.current_candidate_id)
        )
        video_candidate = video_candidate_result.scalar_one()
        video_clips = video_candidate.content.get("generated_clips", [])

        # 获取阶段7音频
        audio_stage_result = await db.execute(
            select(Stage).where(
                Stage.project_id == project.id,
                Stage.stage_type == StageType.AUDIO.value,
            )
        )
        audio_stage = audio_stage_result.scalar_one()
        audio_candidate_result = await db.execute(
            select(Candidate).where(Candidate.id == audio_stage.current_candidate_id)
        )
        audio_candidate = audio_candidate_result.scalar_one()
        dialogue_tracks = audio_candidate.content.get("dialogue_tracks", [])
        bgm_tracks = audio_candidate.content.get("bgm_tracks", [])
        sfx_tracks = audio_candidate.content.get("sfx_tracks", [])

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
                    "stage_type": StageType.ROUGH_CUT.value,
                    "progress_current": 0,
                    "progress_total": num_candidates,
                    "status": "generating",
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        candidates: list[Candidate] = []
        for cand_idx in range(num_candidates):
            # 构建时间线
            timeline = self._build_timeline(video_clips, dialogue_tracks, bgm_tracks, sfx_tracks)

            # 收集所有输入文件路径
            input_files = await self._collect_input_files(db, video_clips, dialogue_tracks, bgm_tracks, sfx_tracks)

            output_name = f"rough_cut_{cand_idx}.mp4"
            output_path = project_dir / output_name

            result_path = await ffmpeg_supplier.process(
                input_files=input_files,
                output_path=str(output_path),
                params={
                    "operation": "rough_cut",
                    "timeline": timeline,
                    "resolution": config.get("resolution", "1920x1080"),
                    "fps": config.get("fps", 24),
                    "audio_sample_rate": config.get("audio_sample_rate", 48000),
                },
            )

            output_stat = Path(result_path).stat()
            artifact = Artifact(
                candidate_id=uuid.uuid4(),
                file_type=FileType.VIDEO.value,
                file_path=str(Path(result_path).relative_to(Path(settings.data_dir))),
                file_size=output_stat.st_size,
                mime_type="video/mp4",
                metadata_={"operation": "rough_cut"},
            )
            db.add(artifact)
            await db.flush()

            candidate = Candidate(
                stage_id=stage.id,
                content={
                    "timeline": timeline,
                    "output_format": "mp4",
                    "resolution": config.get("resolution", "1920x1080"),
                    "fps": config.get("fps", 24),
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
                        "stage_type": StageType.ROUGH_CUT.value,
                        "progress_current": cand_idx + 1,
                        "progress_total": num_candidates,
                        "status": "generating",
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

        await db.flush()
        return candidates

    def _build_timeline(
        self,
        video_clips: list[dict[str, Any]],
        dialogue_tracks: list[dict[str, Any]],
        bgm_tracks: list[dict[str, Any]],
        sfx_tracks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """构建多轨时间线"""
        video_items: list[dict[str, Any]] = []
        current_time = 0.0
        for clip in video_clips:
            duration = clip.get("duration_sec", 5.0)
            video_items.append({
                "clip_ref": f"video_shot_{clip['shot_ref']}",
                "artifact_id": clip["artifact_id"],
                "start_sec": current_time,
                "end_sec": current_time + duration,
                "transition_to_next": "crossfade",
                "transition_duration": 0.5,
            })
            current_time += duration

        return [
            {"track": "video", "items": video_items},
            {"track": "dialogue", "items": [
                {"audio_ref": t.get("id", ""), "artifact_id": t["artifact_id"],
                 "start_sec": t["start_sec"], "volume_db": 0}
                for t in dialogue_tracks
            ]},
            {"track": "bgm", "items": [
                {"audio_ref": t.get("id", ""), "artifact_id": t["artifact_id"],
                 "start_sec": t.get("start_sec", 0), "volume_db": -12,
                 "fade_in": 2.0, "fade_out": 3.0}
                for t in bgm_tracks
            ]},
            {"track": "sfx", "items": [
                {"audio_ref": t.get("id", ""), "artifact_id": t["artifact_id"],
                 "start_sec": t["start_sec"], "volume_db": -6}
                for t in sfx_tracks
            ]},
        ]

    async def _collect_input_files(
        self,
        db: AsyncSession,
        video_clips: list[dict[str, Any]],
        dialogue_tracks: list[dict[str, Any]],
        bgm_tracks: list[dict[str, Any]],
        sfx_tracks: list[dict[str, Any]],
    ) -> list[str]:
        """从数据库中解析所有 artifact 的实际文件路径"""
        all_artifact_ids: list[str] = (
            [c["artifact_id"] for c in video_clips]
            + [t["artifact_id"] for t in dialogue_tracks]
            + [t["artifact_id"] for t in bgm_tracks]
            + [t["artifact_id"] for t in sfx_tracks]
        )
        paths: list[str] = []
        for aid in all_artifact_ids:
            result = await db.execute(select(Artifact).where(Artifact.id == aid))
            artifact = result.scalar_one_or_none()
            if artifact:
                full_path = str(Path(settings.data_dir) / artifact.file_path)
                paths.append(full_path)
        return paths