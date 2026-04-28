"""
流水线异步任务。
"""

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app import celery_app
from app.database import async_session_factory
from app.models import Candidate, Stage
from app.suppliers.registry import SupplierRegistry

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.pipeline_tasks.generate_candidates")
def generate_candidates(
    self,
    project_id: str,
    stage_type: str,
    num_candidates: int,
    prompt: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    """
    异步生成候选内容。
    
    Args:
        project_id: 项目ID
        stage_type: 阶段类型
        num_candidates: 候选数量
        prompt: 提示词
        config: 配置参数
    
    Returns:
        包含生成的候选ID的字典
    """
    import asyncio
    from app.services.pipeline_service import generate_candidates as generate_candidates_service
    
    async def _run():
        async with async_session_factory() as db:
            from app.suppliers.registry import SupplierRegistry
            from app.models.project import Project
            
            registry = SupplierRegistry()
            
            proj_result = await db.execute(select(Project).where(Project.id == uuid.UUID(project_id)))
            project = proj_result.scalar_one()
            stage_result = await db.execute(
                select(Stage).where(Stage.project_id == uuid.UUID(project_id), Stage.stage_type == stage_type)
            )
            stage = stage_result.scalar_one()
            
            try:
                result = await generate_candidates_service(
                    db=db,
                    project=project,
                    stage=stage,
                    prompt=prompt,
                    config=config,
                    num_candidates=num_candidates,
                    registry=registry,
                )
                return {
                    "status": "success",
                    "candidate_ids": [str(c.id) for c in result],
                }
            except Exception as e:
                logger.error(f"生成候选失败: {e}", exc_info=True)
                return {
                    "status": "error",
                    "error": str(e),
                }
    
    return asyncio.run(_run())


@celery_app.task(bind=True, name="app.tasks.pipeline_tasks.process_stage")
def process_stage(
    self,
    project_id: str,
    stage_type: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    """
    异步处理整个阶段。
    
    Args:
        project_id: 项目ID
        stage_type: 阶段类型
        config: 配置参数
    
    Returns:
        处理结果
    """
    import asyncio
    from app.services.pipeline_service import PipelineService
    
    async def _run():
        async with async_session_factory() as db:
            pipeline_service = PipelineService(db)
            try:
                result = await pipeline_service.process_stage(
                    project_id=uuid.UUID(project_id),
                    stage_type=stage_type,
                    config=config,
                )
                return {
                    "status": "success",
                    "result": result,
                }
            except Exception as e:
                logger.error(f"处理阶段失败: {e}", exc_info=True)
                return {
                    "status": "error",
                    "error": str(e),
                }
    
    return asyncio.run(_run())


@celery_app.task(bind=True, name="app.tasks.pipeline_tasks.generate_artifact")
def generate_artifact(
    self,
    candidate_id: str,
    artifact_type: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    """
    异步生成候选内容的产物。
    
    Args:
        candidate_id: 候选ID
        artifact_type: 产物类型
        config: 配置参数
    
    Returns:
        生成的产物信息
    """
    import asyncio
    from app.services.pipeline_service import PipelineService
    
    async def _run():
        async with async_session_factory() as db:
            pipeline_service = PipelineService(db)
            try:
                result = await pipeline_service.generate_artifact(
                    candidate_id=uuid.UUID(candidate_id),
                    artifact_type=artifact_type,
                    config=config,
                )
                return {
                    "status": "success",
                    "artifact_id": str(result.id),
                }
            except Exception as e:
                logger.error(f"生成产物失败: {e}", exc_info=True)
                return {
                    "status": "error",
                    "error": str(e),
                }
    
    return asyncio.run(_run())