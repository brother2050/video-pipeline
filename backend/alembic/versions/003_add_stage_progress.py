"""add stage progress fields

Revision ID: 003
Revises: 002
Create Date: 2025-01-01 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("stages", sa.Column("progress_current", sa.Integer, server_default="0"))
    op.add_column("stages", sa.Column("progress_total", sa.Integer, server_default="0"))


def downgrade() -> None:
    op.drop_column("stages", "progress_total")
    op.drop_column("stages", "progress_current")