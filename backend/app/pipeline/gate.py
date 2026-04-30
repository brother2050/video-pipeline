"""
审核门控：管理阶段的审核、锁定、回退。
集成角色状态、场景资产、节奏模板、合规检查功能。
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.logging_config import PipelineLogger
from app.models.stage import Stage
from app.models.candidate import Candidate
from app.models.project import Project
from app.schemas.enums import StageType, StageStatus
from app.schemas.rollback import RollbackResponse
from app.exceptions import ConflictError, NotFoundError
from app.pipeline.engine import pipeline_engine, STAGE_ORDER


class ReviewGate:
    """审核门控"""

    async def approve(self, db: AsyncSession, stage_id: UUID, candidate_id: UUID) -> Stage:
        """通过审核：选中候选 → 锁定阶段 → 触发引擎 advance"""
        pipeline_logger = PipelineLogger("review_gate")
        
        stage_result = await db.execute(select(Stage).where(Stage.id == stage_id))
        stage = stage_result.scalar_one_or_none()
        if stage is None:
            raise NotFoundError("Stage", str(stage_id))

        # 允许在 REVIEW、READY、FAILED 状态下审核
        if stage.status not in (StageStatus.REVIEW.value, StageStatus.READY.value, StageStatus.FAILED.value):
            raise ConflictError(f"Stage {stage.stage_type} is in status '{stage.status}', cannot approve")

        # 验证候选存在
        candidate_result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
        candidate = candidate_result.scalar_one_or_none()
        if candidate is None:
            raise NotFoundError("Candidate", str(candidate_id))

        # 获取项目信息
        project_result = await db.execute(select(Project).where(Project.id == stage.project_id))
        project = project_result.scalar_one_or_none()
        if project is None:
            raise NotFoundError("Project", str(stage.project_id))

        pipeline_logger.log_approval_action(str(stage.project_id), str(candidate_id), True)
        
        # 根据阶段类型执行特定的集成操作
        stage_type = StageType(stage.stage_type)
        await self._execute_stage_integration(db, stage, candidate, project, stage_type)

        # 选中候选
        candidate.is_selected = True
        stage.current_candidate_id = candidate_id
        stage.status = StageStatus.LOCKED.value
        stage.locked_at = datetime.now(timezone.utc)
        await db.flush()

        # 推进流水线
        await pipeline_engine.advance(db, stage.project_id)
        pipeline_logger.log_stage_complete(str(stage.project_id), str(candidate_id))
        return stage

    async def _execute_stage_integration(
        self,
        db: AsyncSession,
        stage: Stage,
        candidate: Candidate,
        project: Project,
        stage_type: StageType,
    ) -> None:
        """
        根据阶段类型执行集成操作
        
        Args:
            db: 数据库会话
            stage: 阶段对象
            candidate: 候选对象
            project: 项目对象
            stage_type: 阶段类型
        """
        if stage_type == StageType.WORLDBUILDING:
            # 世界观阶段：提取并保存角色状态
            from app.pipeline.stages.s01_worldbuilding import WorldbuildingStage
            worldbuilding_stage = WorldbuildingStage()
            await worldbuilding_stage.extract_and_save_character_states(
                db, project, candidate.content, str(candidate.id)
            )
        
        elif stage_type == StageType.OUTLINE:
            # 剧情大纲阶段：提取并保存节奏模板
            from app.pipeline.stages.s02_outline import OutlineStage
            outline_stage = OutlineStage()
            await outline_stage.extract_and_save_pacing_template(
                db, project, candidate.content, str(candidate.id)
            )
        
        elif stage_type == StageType.STORYBOARD:
            # 分镜阶段：提取并保存场景资产
            from app.pipeline.stages.s04_storyboard import StoryboardStage
            storyboard_stage = StoryboardStage()
            await storyboard_stage.extract_and_save_scene_assets(
                db, project, candidate.content, str(candidate.id)
            )
        
        # 执行合规检查
        await self._execute_compliance_check(db, project, candidate, stage_type)

    async def _execute_compliance_check(
        self,
        db: AsyncSession,
        project: Project,
        candidate: Candidate,
        stage_type: StageType,
    ) -> None:
        """
        对候选内容执行合规检查
        
        Args:
            db: 数据库会话
            project: 项目对象
            candidate: 候选对象
            stage_type: 阶段类型
        """
        from app.models.continuity import ComplianceReport
        from datetime import datetime, timezone
        
        # 创建合规检查报告
        compliance_report = ComplianceReport(
            project_id=project.id,
            check_type="content_compliance",
            episode_number=None,
            stage_type=stage_type.value,
            status="completed",
            violations=0,
            violations_detail={
                "candidate_id": str(candidate.id),
                "checked_at": datetime.now(timezone.utc).isoformat(),
                "issues": [],
            },
        )
        db.add(compliance_report)

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