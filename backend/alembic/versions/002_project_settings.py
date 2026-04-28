"""add project_settings table

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "project_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("projects.id", ondelete="CASCADE"),
                  unique=True, nullable=False),
        sa.Column("default_num_candidates", sa.Integer, server_default="3"),
        sa.Column("image_width", sa.Integer, server_default="1536"),
        sa.Column("image_height", sa.Integer, server_default="864"),
        sa.Column("video_resolution", sa.String(20), server_default="1920x1080"),
        sa.Column("video_fps", sa.Integer, server_default="24"),
        sa.Column("video_duration_sec", sa.Float, server_default="5.0"),
        sa.Column("default_tts_voice", sa.String(100), server_default="default"),
        sa.Column("default_bgm_style", sa.String(200), server_default=""),
        sa.Column("default_sfx_library", sa.String(200), server_default=""),
        sa.Column("output_bitrate", sa.String(20), server_default="8M"),
        sa.Column("output_audio_codec", sa.String(20), server_default="aac"),
        sa.Column("output_audio_bitrate", sa.String(20), server_default="192k"),
        sa.Column("subtitle_enabled", sa.Boolean, server_default="true"),
        sa.Column("subtitle_font", sa.String(100), server_default="Noto Sans SC"),
        sa.Column("subtitle_size", sa.Integer, server_default="48"),
        sa.Column("subtitle_color", sa.String(20), server_default="white"),
        sa.Column("subtitle_position", sa.String(30), server_default="bottom_center"),
        sa.Column("color_grade_lut", sa.String(200), server_default=""),
        sa.Column("color_grade_intensity", sa.Float, server_default="0.8"),
        sa.Column("vignette_intensity", sa.Float, server_default="0.3"),
        sa.Column("grain_intensity", sa.Float, server_default="0.05"),
        sa.Column("preferred_suppliers", postgresql.JSONB, server_default="{}"),
        sa.Column("comfyui_workflow_path", sa.String(500), server_default=""),
        sa.Column("extra", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("project_settings")