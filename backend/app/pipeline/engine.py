"""
流水线引擎：管理 9 个阶段的推进、回退、状态查询。
"""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.stage import Stage
from app.schemas.enums import StageType, StageStatus


# 阶段顺序
STAGE_ORDER: list[StageType] = [
    StageType.WORLDBUILDING,
    StageType.OUTLINE,
    StageType.SCRIPT,
    StageType.STORYBOARD,
    StageType.KEYFRAME,
    StageType.VIDEO,
    StageType.AUDIO,
    StageType.ROUGH_CUT,
    StageType.FINAL_CUT,
]


class PipelineEngine:
    """流水线引擎"""

    async def initialize_project(self, db: AsyncSession, project: Project) -> list[Stage]:
        """创建项目时初始化 9 个阶段，第一个设为 READY，其余 PENDING"""
        stages: list[Stage] = []
        for i, stage_type in enumerate(STAGE_ORDER):
            status = StageStatus.READY if i == 0 else StageStatus.PENDING
            stage = Stage(
                project_id=project.id,
                stage_type=stage_type.value,
                status=status.value,
                prompt="",
                config={},
            )
            db.add(stage)
            stages.append(stage)
        await db.flush()
        return stages

    async def can_start(self, db: AsyncSession, project_id: UUID, stage_type: StageType) -> bool:
        """检查是否可以开始指定阶段（前置阶段必须已 LOCKED）"""
        idx = STAGE_ORDER.index(stage_type)
        if idx == 0:
            return True
        prev_type = STAGE_ORDER[idx - 1]
        result = await db.execute(
            select(Stage).where(
                Stage.project_id == project_id,
                Stage.stage_type == prev_type.value,
            )
        )
        prev_stage = result.scalar_one_or_none()
        return prev_stage is not None and prev_stage.status == StageStatus.LOCKED.value

    async def advance(self, db: AsyncSession, project_id: UUID) -> StageType | None:
        """当前阶段锁定后，将下一阶段从 PENDING 改为 READY。返回解锁的阶段类型。"""
        project_result = await db.execute(select(Project).where(Project.id == project_id))
        project = project_result.scalar_one()
        current_idx = next(
            (i for i, st in enumerate(STAGE_ORDER) if st.value == project.current_stage), 0
        )
        if current_idx + 1 < len(STAGE_ORDER):
            next_type = STAGE_ORDER[current_idx + 1]
            next_stage_result = await db.execute(
                select(Stage).where(
                    Stage.project_id == project_id,
                    Stage.stage_type == next_type.value,
                )
            )
            next_stage = next_stage_result.scalar_one_or_none()
            if next_stage and next_stage.status == StageStatus.PENDING.value:
                next_stage.status = StageStatus.READY.value
                project.current_stage = next_type.value
                await db.flush()
                return next_type
        return None

    async def rollback(
        self, db: AsyncSession, project_id: UUID, target: StageType
    ) -> list[StageType]:
        """回退到 target 阶段，将 target 及之后的所有阶段重置。返回受影响列表。"""
        target_idx = STAGE_ORDER.index(target)
        affected: list[StageType] = []

        for stage_type in STAGE_ORDER[target_idx:]:
            result = await db.execute(
                select(Stage).where(
                    Stage.project_id == project_id,
                    Stage.stage_type == stage_type.value,
                )
            )
            stage = result.scalar_one_or_none()
            if stage:
                if stage_type == target:
                    stage.status = StageStatus.READY.value
                    stage.current_candidate_id = None
                    stage.locked_at = None
                else:
                    stage.status = StageStatus.PENDING.value
                    stage.current_candidate_id = None
                    stage.locked_at = None
                affected.append(stage_type)

        # 更新项目当前阶段
        project_result = await db.execute(select(Project).where(Project.id == project_id))
        project = project_result.scalar_one()
        project.current_stage = target.value
        await db.flush()
        return affected

    async def get_status(self, db: AsyncSession, project_id: UUID) -> list[Stage]:
        """返回所有 9 个阶段"""
        result = await db.execute(
            select(Stage).where(Stage.project_id == project_id).order_by(Stage.stage_type)
        )
        return list(result.scalars().all())

    def get_rollback_impact(self, target: StageType) -> list[StageType]:
        """计算回退到 target 会影响哪些阶段（不访问数据库）"""
        target_idx = STAGE_ORDER.index(target)
        return STAGE_ORDER[target_idx:]


# 全局单例
pipeline_engine = PipelineEngine()
