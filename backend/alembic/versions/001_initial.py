"""initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import sqlite, postgresql

from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 根据数据库类型选择合适的类型
    is_sqlite = op.get_context().dialect.name == 'sqlite'
    uuid_type = sa.UUID if is_sqlite else postgresql.UUID(as_uuid=True)
    json_type = sa.JSON if is_sqlite else postgresql.JSONB
    
    # projects
    op.create_table(
        "projects",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, server_default=""),
        sa.Column("genre", sa.String(100), server_default=""),
        sa.Column("target_episodes", sa.Integer, server_default="1"),
        sa.Column("target_duration_minutes", sa.Integer, server_default="30"),
        sa.Column("current_stage", sa.String(50), server_default="worldbuilding"),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # candidates (先于 stages，因为 stages 有 FK 指向 candidates)
    op.create_table(
        "candidates",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("stage_id", uuid_type, nullable=False),
        sa.Column("content", json_type, server_default="{}"),
        sa.Column("metadata", json_type, server_default="{}"),
        sa.Column("is_selected", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # stages
    op.create_table(
        "stages",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("project_id", uuid_type, sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stage_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("prompt", sa.Text, server_default=""),
        sa.Column("config", json_type, server_default="{}"),
        sa.Column("current_candidate_id", uuid_type, sa.ForeignKey("candidates.id"), nullable=True),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("project_id", "stage_type", name="uq_project_stage"),
    )

    # artifacts
    op.create_table(
        "artifacts",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("candidate_id", uuid_type, sa.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_type", sa.String(50), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("file_size", sa.BigInteger, server_default="0"),
        sa.Column("mime_type", sa.String(100), server_default="application/octet-stream"),
        sa.Column("metadata", json_type, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # versions
    op.create_table(
        "versions",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("stage_id", uuid_type, sa.ForeignKey("stages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer, nullable=False),
        sa.Column("content_snapshot", json_type, server_default="{}"),
        sa.Column("prompt_snapshot", sa.Text, server_default=""),
        sa.Column("diff_summary", sa.Text, nullable=True),
        sa.Column("created_by", sa.String(50), server_default="user"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # nodes
    op.create_table(
        "nodes",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("host", sa.String(255), nullable=False),
        sa.Column("port", sa.Integer, nullable=False),
        sa.Column("capabilities", json_type, server_default="[]"),
        sa.Column("models", json_type, server_default="[]"),
        sa.Column("tags", json_type, server_default="{}"),
        sa.Column("enabled", sa.Boolean, server_default="true"),
        sa.Column("status", sa.String(50), server_default="offline"),
        sa.Column("last_heartbeat", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # capability_configs
    op.create_table(
        "capability_configs",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("capability", sa.String(50), unique=True, nullable=False),
        sa.Column("suppliers", json_type, server_default="[]"),
        sa.Column("retry_count", sa.Integer, server_default="2"),
        sa.Column("timeout_seconds", sa.Integer, server_default="60"),
        sa.Column("local_timeout_seconds", sa.Integer, server_default="300"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("capability_configs")
    op.drop_table("nodes")
    op.drop_table("versions")
    op.drop_table("artifacts")
    op.drop_table("stages")
    op.drop_table("candidates")
    op.drop_table("projects")