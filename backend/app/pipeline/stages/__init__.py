"""
导出所有阶段实例。
"""

from app.pipeline.stages.base import BaseStage
from app.pipeline.stages.s01_worldbuilding import WorldbuildingStage
from app.pipeline.stages.s02_outline import OutlineStage
from app.pipeline.stages.s03_script import ScriptStage
from app.pipeline.stages.s04_storyboard import StoryboardStage
from app.pipeline.stages.s05_keyframe import KeyframeStage
from app.pipeline.stages.s06_video import VideoStage
from app.pipeline.stages.s07_audio import AudioStage
from app.pipeline.stages.s08_rough_cut import RoughCutStage
from app.pipeline.stages.s09_final_cut import FinalCutStage

from app.schemas.enums import StageType

STAGE_IMPLEMENTATIONS: dict[StageType, BaseStage] = {
    StageType.WORLDBUILDING: WorldbuildingStage(),
    StageType.OUTLINE: OutlineStage(),
    StageType.SCRIPT: ScriptStage(),
    StageType.STORYBOARD: StoryboardStage(),
    StageType.KEYFRAME: KeyframeStage(),
    StageType.VIDEO: VideoStage(),
    StageType.AUDIO: AudioStage(),
    StageType.ROUGH_CUT: RoughCutStage(),
    StageType.FINAL_CUT: FinalCutStage(),
}

__all__ = ["BaseStage", "STAGE_IMPLEMENTATIONS"]
