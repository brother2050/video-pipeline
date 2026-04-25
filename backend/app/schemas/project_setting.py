"""
项目设置 Schema。
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProjectSettingResponse(BaseModel):
    id: str
    project_id: str

    # 生成默认值
    default_num_candidates: int
    image_width: int
    image_height: int
    video_resolution: str
    video_fps: int
    video_duration_sec: float

    # 音频默认值
    default_tts_voice: str
    default_bgm_style: str
    default_sfx_library: str

    # 输出设置
    output_bitrate: str
    output_audio_codec: str
    output_audio_bitrate: str

    # 字幕设置
    subtitle_enabled: bool
    subtitle_font: str
    subtitle_size: int
    subtitle_color: str
    subtitle_position: str

    # 调色设置
    color_grade_lut: str
    color_grade_intensity: float
    vignette_intensity: float
    grain_intensity: float

    # 供应商偏好
    preferred_suppliers: dict[str, str]

    # ComfyUI
    comfyui_workflow_path: str

    # 扩展
    extra: dict[str, Any]

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectSettingUpdate(BaseModel):
    """所有字段可选，只传需要修改的"""
    default_num_candidates: int | None = Field(default=None, ge=1, le=10)
    image_width: int | None = Field(default=None, ge=256, le=4096)
    image_height: int | None = Field(default=None, ge=256, le=4096)
    video_resolution: str | None = None
    video_fps: int | None = Field(default=None, ge=1, le=120)
    video_duration_sec: float | None = Field(default=None, ge=1.0, le=300.0)

    default_tts_voice: str | None = None
    default_bgm_style: str | None = None
    default_sfx_library: str | None = None

    output_bitrate: str | None = None
    output_audio_codec: str | None = None
    output_audio_bitrate: str | None = None

    subtitle_enabled: bool | None = None
    subtitle_font: str | None = None
    subtitle_size: int | None = Field(default=None, ge=12, le=120)
    subtitle_color: str | None = None
    subtitle_position: str | None = None

    color_grade_lut: str | None = None
    color_grade_intensity: float | None = Field(default=None, ge=0.0, le=1.0)
    vignette_intensity: float | None = Field(default=None, ge=0.0, le=1.0)
    grain_intensity: float | None = Field(default=None, ge=0.0, le=1.0)

    preferred_suppliers: dict[str, str] | None = None
    comfyui_workflow_path: str | None = None
    extra: dict[str, Any] | None = None