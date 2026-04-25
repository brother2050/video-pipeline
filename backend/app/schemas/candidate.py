"""
候选 + 素材 Schema。
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.enums import FileType, StageType


class ArtifactResponse(BaseModel):
    id: str
    candidate_id: str
    file_type: FileType
    file_path: str
    file_url: str
    file_size: int
    mime_type: str
    metadata: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class CandidateResponse(BaseModel):
    id: str
    stage_id: str
    stage_type: StageType
    content: dict[str, Any]
    artifacts: list[ArtifactResponse]
    metadata: dict[str, Any]
    is_selected: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CandidateSelectRequest(BaseModel):
    candidate_id: str
