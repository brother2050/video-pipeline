"""
版本历史 Schema。
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class VersionResponse(BaseModel):
    id: str
    stage_id: str
    version_number: int
    content_snapshot: dict[str, Any]
    prompt_snapshot: str
    diff_summary: str | None = None
    created_at: datetime
    created_by: str = "user"

    model_config = {"from_attributes": True}
