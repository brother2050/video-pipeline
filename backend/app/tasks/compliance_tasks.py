"""
合规检查异步任务。
"""

import logging
import uuid
from typing import Any

from app.celery_app import celery_app
from app.database import async_session_factory

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.compliance_tasks.check_face_recognition", queue="compliance")
def check_face_recognition(
    self,
    project_id: str,
    episode_number: int | None = None,
    stage_type: str | None = None,
) -> dict[str, Any]:
    """
    异步执行人脸识别检查。
    
    Args:
        project_id: 项目ID
        episode_number: 集数（可选）
        stage_type: 阶段类型（可选）
    
    Returns:
        检查结果
    """
    import asyncio
    from app.services.compliance_service import ComplianceChecker
    
    async def _run():
        async with async_session_factory() as db:
            try:
                result = await ComplianceChecker().check_face_compliance(
                    db, uuid.UUID(project_id), episode_number, stage_type
                )
                await db.commit()
                return {
                    "status": "success",
                    "report_id": str(result.id),
                }
            except Exception as e:
                logger.error(f"人脸识别检查失败: {e}", exc_info=True)
                await db.rollback()
                return {
                    "status": "error",
                    "error": str(e),
                }
    
    return asyncio.run(_run())


@celery_app.task(bind=True, name="app.tasks.compliance_tasks.check_music_copyright", queue="compliance")
def check_music_copyright(
    self,
    project_id: str,
    episode_number: int | None = None,
    stage_type: str | None = None,
) -> dict[str, Any]:
    """
    异步执行音乐版权检查。
    
    Args:
        project_id: 项目ID
        episode_number: 集数（可选）
        stage_type: 阶段类型（可选）
    
    Returns:
        检查结果
    """
    import asyncio
    from app.services.compliance_service import ComplianceChecker
    
    async def _run():
        async with async_session_factory() as db:
            try:
                result = await ComplianceChecker().check_music_compliance(
                    db, uuid.UUID(project_id), episode_number, stage_type
                )
                await db.commit()
                return {
                    "status": "success",
                    "report_id": str(result.id),
                }
            except Exception as e:
                logger.error(f"音乐版权检查失败: {e}", exc_info=True)
                await db.rollback()
                return {
                    "status": "error",
                    "error": str(e),
                }
    
    return asyncio.run(_run())


@celery_app.task(bind=True, name="app.tasks.compliance_tasks.check_content_moderation", queue="compliance")
def check_content_moderation(
    self,
    project_id: str,
    episode_number: int | None = None,
    stage_type: str | None = None,
) -> dict[str, Any]:
    """
    异步执行内容审核检查。
    
    Args:
        project_id: 项目ID
        episode_number: 集数（可选）
        stage_type: 阶段类型（可选）
    
    Returns:
        检查结果
    """
    import asyncio
    from app.services.compliance_service import ComplianceChecker
    
    async def _run():
        async with async_session_factory() as db:
            try:
                result = await ComplianceChecker().check_content_compliance(
                    db, uuid.UUID(project_id), episode_number, stage_type
                )
                await db.commit()
                return {
                    "status": "success",
                    "report_id": str(result.id),
                }
            except Exception as e:
                logger.error(f"内容审核检查失败: {e}", exc_info=True)
                await db.rollback()
                return {
                    "status": "error",
                    "error": str(e),
                }
    
    return asyncio.run(_run())