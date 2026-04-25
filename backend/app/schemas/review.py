"""
审核请求 Schema。
"""

from pydantic import BaseModel

from app.schemas.enums import ReviewAction


class ReviewRequest(BaseModel):
    action: ReviewAction
    candidate_id: str | None = None
    comment: str | None = None
