"""
阶段7：音频合成（对话 + 背景音乐 + 音效）
LLM 生成规划 → 三种供应商分别生成音频。
"""

import json
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
from app.pipeline.json_schemas import AUDIO_SCHEMA
from app.pipeline.prompts import AUDIO_TEMPLATE, AUDIO_EXAMPLE

if TYPE_CHECKING:
    from app.suppliers.registry import SupplierRegistry
from app.config import settings


class AudioStage(BaseStage):
    stage_type = StageType.AUDIO

    def build_prompt(self, project: Project, previous_contents: dict[str, Any]) -> str:
        return AUDIO_TEMPLATE.format(
            characters_json=json.dumps(previous_contents.get("characters", []), indent=2, ensure_ascii=False),
            scenes_json=json.dumps(previous_contents.get("scenes", []), indent=2, ensure_ascii=False),
            schema=json.dumps(AUDIO_SCHEMA, indent=2, ensure_ascii=False),
            example=AUDIO_EXAMPLE,
        )

    def validate_content(self, content: dict[str, Any]) -> tuple[bool, str | None]:
        required = ["voice_cast", "dialogue_tracks", "bgm_tracks", "sfx_tracks"]
        for key in required:
            if key not in content:
                return False, f"Missing required field: {key}"
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
        from app.services.generation_service import call_llm_for_json
        from app.services.file_service import save_bytes_to_file
        from app.ws.hub import ws_hub
        from datetime import datetime, timezone

        project_dir = Path(settings.data_dir) / "projects" / str(project.id)
        project_dir.mkdir(parents=True, exist_ok=True)

        candidates: list[Candidate] = []
        
        # 初始化进度（每个候选需要完成：1个LLM规划 + 对话音频数 + BGM数 + SFX数）
        total_tasks = 0
        for cand_idx in range(num_candidates):
            # 先获取规划来计算任务数
            plan = await call_llm_for_json(
                registry=registry,
                system_prompt=prompt,
                user_prompt=f"请生成第 {cand_idx + 1} 个音频方案。",
                schema=AUDIO_SCHEMA,
            )
            total_tasks += 1  # LLM规划
            total_tasks += len(plan.get("dialogue_plan", []))  # 对话音频
            total_tasks += len(plan.get("bgm_plan", []))  # 背景音乐
            total_tasks += len(plan.get("sfx_plan", []))  # 音效
        
        stage.progress_total = total_tasks
        stage.progress_current = 0
        await db.flush()

        # 发送初始进度
        await ws_hub.broadcast_to_project(
            str(project.id),
            {
                "type": "stage_progress",
                "data": {
                    "project_id": str(project.id),
                    "stage_type": StageType.AUDIO.value,
                    "progress_current": 0,
                    "progress_total": total_tasks,
                    "status": "generating",
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        current_task = 0
        
        for cand_idx in range(num_candidates):
            # 步骤1: LLM 生成音频规划
            plan = await call_llm_for_json(
                registry=registry,
                system_prompt=prompt,
                user_prompt=f"请生成第 {cand_idx + 1} 个音频方案。",
                schema=AUDIO_SCHEMA,
            )
            
            # 更新进度
            current_task += 1
            stage.progress_current = current_task
            await db.flush()
            
            # 发送进度更新
            await ws_hub.broadcast_to_project(
                str(project.id),
                {
                    "type": "stage_progress",
                    "data": {
                        "project_id": str(project.id),
                        "stage_type": StageType.AUDIO.value,
                        "progress_current": current_task,
                        "progress_total": total_tasks,
                        "status": "generating",
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

            # 步骤2: 生成对话音频
            tts_supplier = await registry.get_with_fallback(SupplierCapability.TTS)
            dialogue_tracks: list[dict[str, Any]] = []
            for dlg in plan.get("dialogue_plan", []):
                voice_id = dlg.get("voice_id", "")
                if not voice_id:
                    character = dlg.get("character", "")
                    voice_cast = plan.get("voice_cast", {})
                    voice_id = voice_cast.get(character, {}).get("voice_id", "default")

                audio_bytes = await tts_supplier.synthesize(
                    text=dlg["text"],
                    voice_id=voice_id,
                    emotion=dlg.get("emotion", "neutral"),
                )

                file_name = f"dlg_s{dlg['scene_ref']}_{dlg['character']}_{cand_idx}.wav"
                artifact = await save_bytes_to_file(
                    db=db,
                    candidate_id=uuid.uuid4(),
                    data=audio_bytes,
                    file_path=project_dir / file_name,
                    file_type=FileType.AUDIO,
                    mime_type="audio/wav",
                    metadata={"scene_ref": dlg["scene_ref"], "character": dlg["character"]},
                )
                dialogue_tracks.append({
                    **dlg,
                    "artifact_id": str(artifact.id),
                })

                # 更新进度
                current_task += 1
                stage.progress_current = current_task
                await db.flush()
                
                # 发送进度更新
                await ws_hub.broadcast_to_project(
                    str(project.id),
                    {
                        "type": "stage_progress",
                        "data": {
                            "project_id": str(project.id),
                            "stage_type": StageType.AUDIO.value,
                            "progress_current": current_task,
                            "progress_total": total_tasks,
                            "status": "generating",
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                )

            # 步骤3: 生成背景音乐
            bgm_supplier = await registry.get_with_fallback(SupplierCapability.BGM)
            bgm_tracks: list[dict[str, Any]] = []
            for bgm in plan.get("bgm_plan", []):
                audio_bytes = await bgm_supplier.generate_bgm(
                    prompt=f"{bgm['style']}, {bgm['mood']}",
                    duration_sec=bgm["duration_sec"],
                )
                file_name = f"bgm_s{bgm['scene_ref']}_{cand_idx}.wav"
                artifact = await save_bytes_to_file(
                    db=db,
                    candidate_id=uuid.uuid4(),
                    data=audio_bytes,
                    file_path=project_dir / file_name,
                    file_type=FileType.AUDIO,
                    mime_type="audio/wav",
                    metadata={"scene_ref": bgm["scene_ref"], "style": bgm["style"]},
                )
                bgm_tracks.append({**bgm, "artifact_id": str(artifact.id)})

                # 更新进度
                current_task += 1
                stage.progress_current = current_task
                await db.flush()
                
                # 发送进度更新
                await ws_hub.broadcast_to_project(
                    str(project.id),
                    {
                        "type": "stage_progress",
                        "data": {
                            "project_id": str(project.id),
                            "stage_type": StageType.AUDIO.value,
                            "progress_current": current_task,
                            "progress_total": total_tasks,
                            "status": "generating",
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                )

            # 步骤4: 生成音效
            sfx_supplier = await registry.get_with_fallback(SupplierCapability.SFX)
            sfx_tracks: list[dict[str, Any]] = []
            for sfx in plan.get("sfx_plan", []):
                audio_bytes = await sfx_supplier.generate_sfx(
                    prompt=sfx["description"],
                    duration_sec=sfx["duration_sec"],
                )
                safe_name = sfx["description"][:20].replace(" ", "_")
                file_name = f"sfx_s{sfx['scene_ref']}_{safe_name}_{cand_idx}.wav"
                artifact = await save_bytes_to_file(
                    db=db,
                    candidate_id=uuid.uuid4(),
                    data=audio_bytes,
                    file_path=project_dir / file_name,
                    file_type=FileType.AUDIO,
                    mime_type="audio/wav",
                    metadata={"scene_ref": sfx["scene_ref"], "description": sfx["description"]},
                )
                sfx_tracks.append({**sfx, "artifact_id": str(artifact.id)})

                # 更新进度
                current_task += 1
                stage.progress_current = current_task
                await db.flush()
                
                # 发送进度更新
                await ws_hub.broadcast_to_project(
                    str(project.id),
                    {
                        "type": "stage_progress",
                        "data": {
                            "project_id": str(project.id),
                            "stage_type": StageType.AUDIO.value,
                            "progress_current": current_task,
                            "progress_total": total_tasks,
                            "status": "generating",
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                )

            # 步骤5: 组装候选
            content = {
                "voice_cast": plan.get("voice_cast", {}),
                "dialogue_tracks": dialogue_tracks,
                "bgm_tracks": bgm_tracks,
                "sfx_tracks": sfx_tracks,
            }
            candidate = Candidate(
                stage_id=stage.id,
                content=content,
                metadata_={"candidate_index": cand_idx},
            )
            db.add(candidate)
            candidates.append(candidate)

        await db.flush()
        return candidates