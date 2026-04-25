"""
阶段相关 Schema。
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.enums import StageStatus, StageType


class StageResponse(BaseModel):
    id: str
    project_id: str
    stage_type: StageType
    status: StageStatus
    prompt: str
    config: dict[str, Any]
    current_candidate_id: str | None = None
    locked_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StageGenerateRequest(BaseModel):
    prompt: str | None = None
    config: dict[str, Any] | None = None
    num_candidates: int = Field(default=3, ge=1, le=10)


class StagePromptUpdate(BaseModel):
    prompt: str


class StageConfigUpdate(BaseModel):
    config: dict[str, Any]
