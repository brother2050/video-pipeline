"""
审核服务：封装审核门控操作。
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stage import Stage
from app.schemas.enums import ReviewAction
from app.pipeline.gate import review_gate
from app.services.version_service import create_version_snapshot
from app.exceptions import ValidationError


async def handle_review(
    db: AsyncSession,
    stage: Stage,
    action: ReviewAction,
    candidate_id: UUID | None,
    comment: str,
) -> Stage:
    """处理审核操作"""
    # 创建版本快照
    await create_version_snapshot(db, stage, created_by="review")

    if action == ReviewAction.APPROVE:
        if candidate_id is None:
            raise ValidationError("candidate_id is required for approve action")
        return await review_gate.approve(db, stage.id, candidate_id)
    elif action == ReviewAction.REJECT:
        return await review_gate.reject(db, stage.id, comment)
    elif action == ReviewAction.REGENERATE:
        return await review_gate.regenerate(db, stage.id, stage.prompt, stage.config)
    else:
        raise ValidationError(f"Unknown review action: {action}")
