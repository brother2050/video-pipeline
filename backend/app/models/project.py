"""
Project SQLAlchemy 模型。
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    genre: Mapped[str] = mapped_column(String(100), default="")
    target_episodes: Mapped[int] = mapped_column(Integer, default=1)
    target_duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    current_stage: Mapped[str] = mapped_column(String(50), default="worldbuilding")
    status: Mapped[str] = mapped_column(String(50), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # 关系
    stages: Mapped[list["Stage"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", lazy="selectin"
    )
    settings: Mapped["ProjectSetting"] = relationship(
        back_populates="project", cascade="all, delete-orphan", uselist=False
    )


class ProjectSetting(Base):
    __tablename__ = "project_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # --- 生成默认值 ---
    default_num_candidates: Mapped[int] = mapped_column(default=3)
    image_width: Mapped[int] = mapped_column(default=1536)
    image_height: Mapped[int] = mapped_column(default=864)
    video_resolution: Mapped[str] = mapped_column(String(20), default="1920x1080")
    video_fps: Mapped[int] = mapped_column(default=24)
    video_duration_sec: Mapped[float] = mapped_column(default=5.0)

    # --- 音频默认值 ---
    default_tts_voice: Mapped[str] = mapped_column(String(100), default="default")
    default_bgm_style: Mapped[str] = mapped_column(String(200), default="")
    default_sfx_library: Mapped[str] = mapped_column(String(200), default="")

    # --- 输出设置 ---
    output_bitrate: Mapped[str] = mapped_column(String(20), default="8M")
    output_audio_codec: Mapped[str] = mapped_column(String(20), default="aac")
    output_audio_bitrate: Mapped[str] = mapped_column(String(20), default="192k")

    # --- 字幕设置 ---
    subtitle_enabled: Mapped[bool] = mapped_column(default=True)
    subtitle_font: Mapped[str] = mapped_column(String(100), default="Noto Sans SC")
    subtitle_size: Mapped[int] = mapped_column(default=48)
    subtitle_color: Mapped[str] = mapped_column(String(20), default="white")
    subtitle_position: Mapped[str] = mapped_column(String(30), default="bottom_center")

    # --- 调色设置 ---
    color_grade_lut: Mapped[str] = mapped_column(String(200), default="")
    color_grade_intensity: Mapped[float] = mapped_column(default=0.8)
    vignette_intensity: Mapped[float] = mapped_column(default=0.3)
    grain_intensity: Mapped[float] = mapped_column(default=0.05)

    # --- 供应商偏好（覆盖全局配置） ---
    preferred_suppliers: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    # 格式: {"llm": "deepseek", "image": "comfyui", "video": "local_video", ...}

    # --- ComfyUI 工作流偏好 ---
    comfyui_workflow_path: Mapped[str] = mapped_column(String(500), default="")

    # --- 扩展字段 ---
    extra: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # 关系
    project: Mapped["Project"] = relationship(back_populates="settings")