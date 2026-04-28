"""add continuity management tables

Revision ID: 004
Revises: 003
Create Date: 2025-01-01 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "character_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("character_name", sa.String(100), nullable=False),
        sa.Column("episode_start", sa.Integer(), nullable=False),
        sa.Column("episode_end", sa.Integer(), nullable=True),
        sa.Column("outfit_description", sa.Text(), server_default=""),
        sa.Column("hairstyle", sa.String(200), server_default=""),
        sa.Column("accessories", sa.JSON(), server_default="{}"),
        sa.Column("makeup", sa.String(200), server_default=""),
        sa.Column("age_appearance", sa.String(100), server_default=""),
        sa.Column("lora_path", sa.String(500), nullable=True),
        sa.Column("embedding_path", sa.String(500), nullable=True),
        sa.Column("reference_image_path", sa.String(500), nullable=True),
        sa.Column("signature_items", sa.JSON(), server_default="{}"),
        sa.Column("notes", sa.Text(), server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    op.create_table(
        "scene_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scene_name", sa.String(200), nullable=False),
        sa.Column("scene_type", sa.String(50), server_default="interior"),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("layout_description", sa.Text(), server_default=""),
        sa.Column("lora_path", sa.String(500), nullable=True),
        sa.Column("controlnet_depth_path", sa.String(500), nullable=True),
        sa.Column("controlnet_edge_path", sa.String(500), nullable=True),
        sa.Column("variants", sa.JSON(), server_default="{}"),
        sa.Column("reference_image_path", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    op.create_table(
        "pacing_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("genre", sa.String(100), server_default=""),
        sa.Column("structure", sa.JSON(), server_default="{}"),
        sa.Column("hook_3sec_config", sa.JSON(), server_default="{}"),
        sa.Column("cliffhanger_config", sa.JSON(), server_default="{}"),
        sa.Column("target_duration_sec", sa.Integer(), server_default=60),
        sa.Column("usage_count", sa.Integer(), server_default=0),
        sa.Column("avg_completion_rate", sa.Float(), server_default=0.0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    op.create_table(
        "consistency_checks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("check_type", sa.String(50), nullable=False),
        sa.Column("episode_start", sa.Integer(), nullable=False),
        sa.Column("episode_end", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("issues_found", sa.Integer(), server_default=0),
        sa.Column("issues_detail", sa.JSON(), server_default="{}"),
        sa.Column("checked_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    op.create_table(
        "compliance_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("check_type", sa.String(50), nullable=False),
        sa.Column("episode_number", sa.Integer(), nullable=True),
        sa.Column("stage_type", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("violations", sa.Integer(), server_default=0),
        sa.Column("violations_detail", sa.JSON(), server_default="{}"),
        sa.Column("checked_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("compliance_reports")
    op.drop_table("consistency_checks")
    op.drop_table("pacing_templates")
    op.drop_table("scene_assets")
    op.drop_table("character_states")