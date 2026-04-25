"""
回滚相关 Schema。
"""

from pydantic import BaseModel

from app.schemas.enums import StageType


class RollbackRequest(BaseModel):
    target_stage: StageType


class RollbackResponse(BaseModel):
    affected_stages: list[StageType]
    message: str
