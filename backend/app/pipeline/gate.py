"""
审核门控：管理阶段的审核、锁定、回退。
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stage import Stage
from app.models.candidate import Candidate
from app.schemas.enums import StageType, StageStatus
from app.schemas.rollback import RollbackResponse
from app.exceptions import ConflictError, NotFoundError
from app.pipeline.engine import pipeline_engine, STAGE_ORDER


class ReviewGate:
    """审核门控"""

    async def approve(self, db: AsyncSession, stage_id: UUID, candidate_id: UUID) -> Stage:
        """通过审核：选中候选 → 锁定阶段 → 触发引擎 advance"""
        stage_result = await db.execute(select(Stage).where(Stage.id == stage_id))
        stage = stage_result.scalar_one_or_none()
        if stage is None:
            raise NotFoundError("Stage", str(stage_id))

        if stage.status not in (StageStatus.REVIEW.value, StageStatus.READY.value):
            raise ConflictError(f"Stage {stage.stage_type} is in status '{stage.status}', cannot approve")

        # 验证候选存在
        candidate_result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
        candidate = candidate_result.scalar_one_or_none()
        if candidate is None:
            raise NotFoundError("Candidate", str(candidate_id))

        # 选中候选
        candidate.is_selected = True
        stage.current_candidate_id = candidate_id
        stage.status = StageStatus.LOCKED.value
        stage.locked_at = datetime.now(timezone.utc)
        await db.flush()

        # 推进流水线
        await pipeline_engine.advance(db, stage.project_id)
        return stage

    async def reject(self, db: AsyncSession, stage_id: UUID, comment: str) -> Stage:
        """拒绝：阶段回到 REVIEW 状态"""
        stage_result = await db.execute(select(Stage).where(Stage.id == stage_id))
        stage = stage_result.scalar_one_or_none()
        if stage is None:
            raise NotFoundError("Stage", str(stage_id))

        stage.status = StageStatus.REVIEW.value
        await db.flush()
        return stage

    async def regenerate(
        self, db: AsyncSession, stage_id: UUID, prompt: str, config: dict
    ) -> Stage:
        """重新生成：阶段回到 GENERATING 状态"""
        stage_result = await db.execute(select(Stage).where(Stage.id == stage_id))
        stage = stage_result.scalar_one_or_none()
        if stage is None:
            raise NotFoundError("Stage", str(stage_id))

        stage.status = StageStatus.GENERATING.value
        if prompt:
            stage.prompt = prompt
        if config:
            stage.config = config
        await db.flush()
        return stage

    async def calculate_impact(
        self, db: AsyncSession, project_id: UUID, target: StageType
    ) -> RollbackResponse:
        """计算回退影响范围"""
        affected = pipeline_engine.get_rollback_impact(target)
        stage_names = [s.value for s in affected]
        return RollbackResponse(
            affected_stages=affected,
            message=f"回退到 {target.value} 将重置以下阶段: {', '.join(stage_names)}",
        )


# 全局单例
review_gate = ReviewGate()
