"""
状态恢复工具
用于处理中断导致的异常状态
"""

import asyncio
from datetime import datetime, timezone, timedelta
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.logging_config import get_logger
from app.models.stage import Stage
from app.schemas.enums import StageStatus

logger = get_logger(__name__)


class StateRecovery:
    """状态恢复工具类"""
    
    # 超时时间：如果阶段在生成中状态超过这个时间，视为异常
    GENERATING_TIMEOUT_MINUTES = 5  # 降低到5分钟，让失败状态更快显示
    
    @classmethod
    async def check_and_recover_stuck_stages(cls) -> dict[str, int]:
        """
        检查并恢复卡住的阶段
        
        Returns:
            包含恢复统计的字典
        """
        logger.info("开始检查卡住的阶段...")
        
        stats = {
            "checked": 0,
            "recovered": 0,
            "skipped": 0,
        }
        
        timeout_threshold = datetime.now(timezone.utc) - timedelta(minutes=cls.GENERATING_TIMEOUT_MINUTES)
        
        async with async_session_factory() as db:
            # 查找所有处于生成中状态的阶段
            stmt = select(Stage).where(Stage.status == StageStatus.GENERATING.value)
            result = await db.execute(stmt)
            stuck_stages = result.scalars().all()
            
            stats["checked"] = len(stuck_stages)
            
            if not stuck_stages:
                logger.info("没有发现卡住的阶段")
                return stats
            
            logger.warning(f"发现 {len(stuck_stages)} 个处于生成中状态的阶段")
            
            for stage in stuck_stages:
                # 检查是否超时
                if stage.updated_at and stage.updated_at < timeout_threshold:
                    logger.warning(
                        f"阶段 {stage.stage_type} (项目: {stage.project_id}) "
                        f"已卡在生成中状态超过 {cls.GENERATING_TIMEOUT_MINUTES} 分钟，"
                        f"最后更新时间: {stage.updated_at}"
                    )
                    
                    # 恢复到就绪状态
                    await cls._recover_stage(db, stage)
                    stats["recovered"] += 1
                else:
                    logger.debug(
                        f"阶段 {stage.stage_type} (项目: {stage.project_id}) "
                        f"仍在正常生成中，最后更新: {stage.updated_at}"
                    )
                    stats["skipped"] += 1
            
            await db.commit()
        
        logger.info(f"状态恢复完成 - 检查: {stats['checked']}, 恢复: {stats['recovered']}, 跳过: {stats['skipped']}")
        return stats
    
    @classmethod
    async def _recover_stage(cls, db: AsyncSession, stage: Stage) -> None:
        """
        恢复单个阶段的状态
        
        Args:
            db: 数据库会话
            stage: 需要恢复的阶段
        """
        # 检查是否有已生成的候选
        from app.models.candidate import Candidate
        
        candidate_stmt = select(Candidate).where(Candidate.stage_id == stage.id)
        candidate_result = await db.execute(candidate_stmt)
        candidates = candidate_result.scalars().all()
        
        if candidates:
            # 如果有候选，恢复到审核状态
            logger.info(f"恢复阶段 {stage.stage_type} 到审核状态 (有 {len(candidates)} 个候选)")
            stage.status = StageStatus.REVIEW.value
        else:
            # 如果没有候选，恢复到就绪状态
            logger.info(f"恢复阶段 {stage.stage_type} 到就绪状态 (无候选)")
            stage.status = StageStatus.READY.value
        
        stage.updated_at = datetime.now(timezone.utc)
        await db.flush()
    
    @classmethod
    async def recover_stage_by_id(
        cls, 
        project_id: UUID, 
        stage_type: str,
        target_status: StageStatus = StageStatus.READY
    ) -> bool:
        """
        手动恢复指定阶段的状态
        
        Args:
            project_id: 项目ID
            stage_type: 阶段类型
            target_status: 目标状态，默认为READY
        
        Returns:
            是否成功恢复
        """
        logger.info(f"手动恢复阶段 - 项目: {project_id}, 阶段: {stage_type}, 目标状态: {target_status.value}")
        
        async with async_session_factory() as db:
            stmt = select(Stage).where(
                Stage.project_id == project_id,
                Stage.stage_type == stage_type
            )
            result = await db.execute(stmt)
            stage = result.scalar_one_or_none()
            
            if not stage:
                logger.error(f"未找到阶段 - 项目: {project_id}, 阶段: {stage_type}")
                return False
            
            logger.info(
                f"恢复阶段状态 - "
                f"项目: {project_id}, "
                f"阶段: {stage_type}, "
                f"当前状态: {stage.status}, "
                f"目标状态: {target_status.value}"
            )
            
            stage.status = target_status.value
            stage.updated_at = datetime.now(timezone.utc)
            await db.commit()
            
            logger.info(f"阶段状态已更新 - 项目: {project_id}, 阶段: {stage_type}")
            return True
    
    @classmethod
    async def get_stuck_stages(cls) -> list[dict[str, any]]:
        """
        获取所有卡住的阶段信息
        
        Returns:
            卡住阶段的信息列表
        """
        timeout_threshold = datetime.now(timezone.utc) - timedelta(minutes=cls.GENERATING_TIMEOUT_MINUTES)
        
        async with async_session_factory() as db:
            stmt = select(Stage).where(
                Stage.status == StageStatus.GENERATING.value,
                Stage.updated_at < timeout_threshold
            )
            result = await db.execute(stmt)
            stuck_stages = result.scalars().all()
            
            return [
                {
                    "project_id": str(stage.project_id),
                    "stage_type": stage.stage_type,
                    "current_status": stage.status,
                    "last_updated": stage.updated_at.isoformat() if stage.updated_at else None,
                    "stuck_duration_minutes": (
                        (datetime.now(timezone.utc) - stage.updated_at).total_seconds() / 60
                        if stage.updated_at else None
                    ),
                }
                for stage in stuck_stages
            ]