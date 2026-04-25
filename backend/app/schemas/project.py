"""
项目相关 Schema。
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.enums import StageStatus, StageType


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    genre: str = Field(default="", max_length=100)
    target_episodes: int = Field(default=1, ge=1, le=100)
    target_duration_minutes: int = Field(default=30, ge=1, le=600)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    genre: str | None = None
    target_episodes: int | None = None
    target_duration_minutes: int | None = None


class StageSummary(BaseModel):
    stage_type: StageType
    status: StageStatus
    has_candidates: bool
    candidate_count: int


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    genre: str
    target_episodes: int
    target_duration_minutes: int
    current_stage: StageType
    status: str
    stages_summary: list[StageSummary]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectDetail(ProjectResponse):
    stages: list["StageResponse"] = []


# 解析前向引用
from app.schemas.stage import StageResponse  # noqa: E402
ProjectDetail.model_rebuild()
