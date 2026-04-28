"""
连续性检查异步任务。
"""

import logging
import uuid
from typing import Any

from app.celery_app import celery_app
from app.database import get_async_session_factory

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.continuity_tasks.check_character_consistency", queue="continuity")
def check_character_consistency(
    self,
    project_id: str,
    episode_start: int = 1,
    episode_end: int = 1,
) -> dict[str, Any]:
    """
    异步执行角色连续性检查。
    
    Args:
        project_id: 项目ID
        episode_start: 起始集数（默认1）
        episode_end: 结束集数（默认1）
    
    Returns:
        检查结果
    """
    import asyncio
    from app.services.continuity_service import consistency_manager
    
    async def _run():
        async with get_async_session_factory()() as db:
            try:
                result = await consistency_manager.check_character_consistency(
                    db=db,
                    project_id=uuid.UUID(project_id),
                    episode_start=episode_start,
                    episode_end=episode_end,
                )
                return {
                    "status": "success",
                    "check_id": str(result.id),
                }
            except Exception as e:
                logger.error(f"角色连续性检查失败: {e}", exc_info=True)
                return {
                    "status": "error",
                    "error": str(e),
                }
    
    return asyncio.run(_run())


@celery_app.task(bind=True, name="app.tasks.continuity_tasks.check_scene_consistency", queue="continuity")
def check_scene_consistency(
    self,
    project_id: str,
    episode_start: int = 1,
    episode_end: int = 1,
) -> dict[str, Any]:
    """
    异步执行场景连续性检查。
    
    Args:
        project_id: 项目ID
        episode_start: 起始集数（默认1）
        episode_end: 结束集数（默认1）
    
    Returns:
        检查结果
    """
    import asyncio
    from app.services.continuity_service import consistency_manager
    
    async def _run():
        async with get_async_session_factory()() as db:
            try:
                result = await consistency_manager.check_scene_consistency(
                    db=db,
                    project_id=uuid.UUID(project_id),
                    episode_start=episode_start,
                    episode_end=episode_end,
                )
                return {
                    "status": "success",
                    "check_id": str(result.id),
                }
            except Exception as e:
                logger.error(f"场景连续性检查失败: {e}", exc_info=True)
                return {
                    "status": "error",
                    "error": str(e),
                }
    
    return asyncio.run(_run())


@celery_app.task(bind=True, name="app.tasks.continuity_tasks.validate_pacing", queue="continuity")
def validate_pacing(
    self,
    project_id: str,
    episode_content: dict[str, Any],
    template_id: str | None = None,
    hook_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    异步执行节奏验证。
    
    Args:
        project_id: 项目ID
        episode_content: 集内容
        template_id: 模板ID（可选）
        hook_config: 钩子配置（可选）
    
    Returns:
        验证结果
    """
    import asyncio
    from app.services.pacing_service import pacing_engine
    from app.models.continuity import PacingTemplate
    from sqlalchemy import select
    
    async def _run():
        async with get_async_session_factory()() as db:
            try:
                template = None
                if template_id:
                    result = await db.execute(
                        select(PacingTemplate).where(PacingTemplate.id == uuid.UUID(template_id))
                    )
                    template = result.scalar_one_or_none()
                
                if not template:
                    return {
                        "status": "error",
                        "error": "Template not found",
                    }
                
                passed, errors = await pacing_engine.validate_pacing(
                    episode_content=episode_content,
                    template=template,
                )
                
                return {
                    "status": "success",
                    "validation_result": {
                        "passed": passed,
                        "errors": errors,
                    },
                }
            except Exception as e:
                logger.error(f"节奏验证失败: {e}", exc_info=True)
                return {
                    "status": "error",
                    "error": str(e),
                }
    
    return asyncio.run(_run())