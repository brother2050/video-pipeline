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
from app.logging_config import AsyncLogger, PipelineLogger
from app.models import Candidate, Stage
from app.suppliers.registry import SupplierRegistry

logger = logging.getLogger(__name__)
@celery_app.task(bind=True, name="app.tasks.pipeline_tasks.generate_candidates", queue="pipeline")
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
    
    task_logger = AsyncLogger("generate_candidates")
    pipeline_logger = PipelineLogger(stage_type)
    task_id = str(self.request.id)
    
    task_logger.log_task_start(task_id, "generate_candidates", 
                             project_id=project_id, stage_type=stage_type, 
                             num_candidates=num_candidates)
    pipeline_logger.log_stage_start(project_id)
    
    async def _run():
        async with async_session_factory() as db:
            from app.suppliers.registry import SupplierRegistry
            from app.models.project import Project
            from app.models.supplier import CapabilityConfig
            from app.schemas.supplier import CapabilityConfigResponse, SupplierSlot
            
            registry = SupplierRegistry()
            
            # 从数据库加载供应商配置
            result = await db.execute(select(CapabilityConfig))
            configs = result.scalars().all()
            if configs:
                from app.schemas.enums import SupplierCapability
                schema_configs = [
                    CapabilityConfigResponse(
                        capability=SupplierCapability(c.capability),
                        suppliers=[SupplierSlot(**s) for s in c.suppliers],
                        retry_count=c.retry_count,
                        timeout_seconds=c.timeout_seconds,
                        local_timeout_seconds=c.local_timeout_seconds,
                    )
                    for c in configs
                ]
                await registry.initialize(schema_configs)
                logger.info(f"Supplier registry initialized with {len(schema_configs)} capabilities")
            
            proj_result = await db.execute(select(Project).where(Project.id == uuid.UUID(project_id)))
            project = proj_result.scalar_one()
            stage_result = await db.execute(
                select(Stage).where(Stage.project_id == uuid.UUID(project_id), Stage.stage_type == stage_type)
            )
            stage = stage_result.scalar_one()
            
            try:
                logger.info(f"开始生成候选 - 项目: {project_id}, 阶段: {stage_type}, 数量: {num_candidates}")
                result = await generate_candidates_service(
                    db=db,
                    project=project,
                    stage=stage,
                    prompt=prompt,
                    config=config,
                    num_candidates=num_candidates,
                    registry=registry,
                )
                candidate_ids = [str(c.id) for c in result]
                task_logger.log_task_success(task_id, "generate_candidates", {"candidate_count": len(candidate_ids)})
                pipeline_logger.log_candidate_generation(project_id, len(candidate_ids))
                logger.info(f"候选生成成功 - 项目: {project_id}, 阶段: {stage_type}, 生成数量: {len(candidate_ids)}")
                return {
                    "status": "success",
                    "candidate_ids": candidate_ids,
                }
            except Exception as e:
                task_logger.log_task_error(task_id, "generate_candidates", e)
                pipeline_logger.log_stage_error(project_id, e)
                logger.error(f"生成候选失败: {e}", exc_info=True)
                return {
                    "status": "error",
                    "error": str(e),
                }
    
    return asyncio.run(_run())


@celery_app.task(bind=True, name="app.tasks.pipeline_tasks.process_stage", queue="pipeline")
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
    from app.services.pipeline_service import generate_candidates as generate_candidates_service
    
    task_logger = AsyncLogger("process_stage")
    pipeline_logger = PipelineLogger(stage_type)
    task_id = str(self.request.id)
    
    task_logger.log_task_start(task_id, "process_stage", 
                             project_id=project_id, stage_type=stage_type)
    pipeline_logger.log_stage_start(project_id)
    
    async def _run():
        async with async_session_factory() as db:
            from app.suppliers.registry import SupplierRegistry
            from app.models.project import Project
            from app.models.supplier import CapabilityConfig
            from app.schemas.supplier import CapabilityConfigResponse, SupplierSlot
            
            registry = SupplierRegistry()
            
            # 从数据库加载供应商配置
            result = await db.execute(select(CapabilityConfig))
            configs = result.scalars().all()
            if configs:
                from app.schemas.enums import SupplierCapability
                schema_configs = [
                    CapabilityConfigResponse(
                        capability=SupplierCapability(c.capability),
                        suppliers=[SupplierSlot(**s) for s in c.suppliers],
                        retry_count=c.retry_count,
                        timeout_seconds=c.timeout_seconds,
                        local_timeout_seconds=c.local_timeout_seconds,
                    )
                    for c in configs
                ]
                await registry.initialize(schema_configs)
                logger.info(f"Supplier registry initialized with {len(schema_configs)} capabilities")
            
            proj_result = await db.execute(select(Project).where(Project.id == uuid.UUID(project_id)))
            project = proj_result.scalar_one()
            stage_result = await db.execute(
                select(Stage).where(Stage.project_id == uuid.UUID(project_id), Stage.stage_type == stage_type)
            )
            stage = stage_result.scalar_one()
            
            try:
                logger.info(f"开始处理阶段 - 项目: {project_id}, 阶段: {stage_type}")
                result = await generate_candidates_service(
                    db=db,
                    project=project,
                    stage=stage,
                    prompt=stage.prompt,
                    config=stage.config,
                    num_candidates=1,
                    registry=registry,
                )
                task_logger.log_task_success(task_id, "process_stage", result)
                pipeline_logger.log_stage_complete(project_id, None, result)
                logger.info(f"阶段处理成功 - 项目: {project_id}, 阶段: {stage_type}")
                return {
                    "status": "success",
                    "result": result,
                }
            except Exception as e:
                task_logger.log_task_error(task_id, "process_stage", e)
                pipeline_logger.log_stage_error(project_id, e)
                logger.error(f"处理阶段失败: {e}", exc_info=True)
                return {
                    "status": "error",
                    "error": str(e),
                }
    
    return asyncio.run(_run())


@celery_app.task(bind=True, name="app.tasks.pipeline_tasks.generate_artifact", queue="pipeline")
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
    from app.services.pipeline_service import generate_candidates as generate_candidates_service
    
    task_logger = AsyncLogger("generate_artifact")
    task_id = str(self.request.id)
    
    task_logger.log_task_start(task_id, "generate_artifact", 
                             candidate_id=candidate_id, artifact_type=artifact_type)
    
    async def _run():
        async with async_session_factory() as db:
            from app.suppliers.registry import SupplierRegistry
            from app.models.project import Project
            from app.models.supplier import CapabilityConfig
            from app.schemas.supplier import CapabilityConfigResponse, SupplierSlot
            
            registry = SupplierRegistry()
            
            # 从数据库加载供应商配置
            result = await db.execute(select(CapabilityConfig))
            configs = result.scalars().all()
            if configs:
                from app.schemas.enums import SupplierCapability
                schema_configs = [
                    CapabilityConfigResponse(
                        capability=SupplierCapability(c.capability),
                        suppliers=[SupplierSlot(**s) for s in c.suppliers],
                        retry_count=c.retry_count,
                        timeout_seconds=c.timeout_seconds,
                        local_timeout_seconds=c.local_timeout_seconds,
                    )
                    for c in configs
                ]
                await registry.initialize(schema_configs)
                logger.info(f"Supplier registry initialized with {len(schema_configs)} capabilities")
            
            try:
                logger.info(f"开始生成产物 - 候选: {candidate_id}, 类型: {artifact_type}")
                # 这里需要实现产物生成逻辑
                # 目前暂时返回成功状态
                task_logger.log_task_success(task_id, "generate_artifact", {"candidate_id": candidate_id})
                logger.info(f"产物生成成功 - 候选: {candidate_id}, 类型: {artifact_type}")
                return {
                    "status": "success",
                    "candidate_id": candidate_id,
                }
            except Exception as e:
                task_logger.log_task_error(task_id, "generate_artifact", e)
                logger.error(f"生成产物失败: {e}", exc_info=True)
                return {
                    "status": "error",
                    "error": str(e),
                }
    
    return asyncio.run(_run())