"""
阶段路由。
"""

import time
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_stage_or_404
from app.logging_config import APILogger, PipelineLogger
from app.models.project import Project
from app.models.stage import Stage
from app.models.candidate import Candidate, Artifact
from app.schemas.common import APIResponse
from app.schemas.enums import StageType, StageStatus, FileType
from app.schemas.stage import (
    StageResponse, StageGenerateRequest, StagePromptUpdate, StageConfigUpdate,
)
from app.schemas.candidate import CandidateResponse, ArtifactResponse, CandidateSelectRequest
from app.schemas.rollback import RollbackRequest, RollbackResponse
from app.schemas.review import ReviewRequest
from app.schemas.version import VersionResponse
from app.services import pipeline_service, review_service, version_service
from app.suppliers.registry import SupplierRegistry
from app.config import settings
from app.ws.hub import ws_hub
from app.tasks.pipeline_tasks import generate_candidates as generate_candidates_task
from datetime import datetime, timezone

router = APIRouter()


def _stage_to_response(stage: Stage) -> StageResponse:
    return StageResponse(
        id=str(stage.id),
        project_id=str(stage.project_id),
        stage_type=StageType(stage.stage_type),
        status=StageStatus(stage.status),
        prompt=stage.prompt,
        config=stage.config or {},
        current_candidate_id=str(stage.current_candidate_id) if stage.current_candidate_id else None,
        locked_at=stage.locked_at,
        created_at=stage.created_at,
        updated_at=stage.updated_at,
    )


def _candidate_to_response(candidate: Candidate, stage_type: str) -> CandidateResponse:
    artifacts = []
    # 安全地访问 artifacts，避免懒加载问题
    try:
        if hasattr(candidate, 'artifacts') and candidate.artifacts:
            for a in candidate.artifacts:
                # 直接使用字符串，避免枚举转换问题
                file_type_str = a.file_type if a.file_type in ["text", "image", "video", "audio", "json"] else "json"
                file_type = FileType(file_type_str)
                
                artifacts.append(ArtifactResponse(
                    id=str(a.id),
                    candidate_id=str(a.candidate_id),
                    file_type=file_type,
                    file_path=a.file_path,
                    file_url=f"/api/files/{a.file_path}",
                    file_size=a.file_size,
                    mime_type=a.mime_type,
                    metadata=a.metadata_ or {},
                    created_at=a.created_at,
                ))
    except Exception:
        # 如果无法加载 artifacts，返回空列表
        pass
    
    return CandidateResponse(
        id=str(candidate.id),
        stage_id=str(candidate.stage_id),
        stage_type=StageType(stage_type),
        content=candidate.content or {},
        artifacts=artifacts,
        metadata=candidate.metadata_ or {},
        is_selected=candidate.is_selected,
        created_at=candidate.created_at,
    )


@router.get("/projects/{project_id}/stages", response_model=APIResponse[list[StageResponse]])
async def list_stages(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[list[StageResponse]]:
    result = await db.execute(
        select(Stage).where(Stage.project_id == project_id)
    )
    stages = list(result.scalars().all())
    return APIResponse(data=[_stage_to_response(s) for s in stages])


@router.get("/projects/{project_id}/stages/{stage_type}", response_model=APIResponse[StageResponse])
async def get_stage(
    project_id: UUID,
    stage_type: str,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[StageResponse]:
    result = await db.execute(
        select(Stage).where(Stage.project_id == project_id, Stage.stage_type == stage_type)
    )
    stage = result.scalar_one()
    return APIResponse(data=_stage_to_response(stage))


@router.put("/projects/{project_id}/stages/{stage_type}/prompt", response_model=APIResponse[StageResponse])
async def update_prompt(
    project_id: UUID,
    stage_type: str,
    data: StagePromptUpdate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[StageResponse]:
    result = await db.execute(
        select(Stage).where(Stage.project_id == project_id, Stage.stage_type == stage_type)
    )
    stage = result.scalar_one()
    stage.prompt = data.prompt
    await db.flush()
    await db.refresh(stage)
    return APIResponse(data=_stage_to_response(stage))


@router.put("/projects/{project_id}/stages/{stage_type}/config", response_model=APIResponse[StageResponse])
async def update_config(
    project_id: UUID,
    stage_type: str,
    data: StageConfigUpdate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[StageResponse]:
    result = await db.execute(
        select(Stage).where(Stage.project_id == project_id, Stage.stage_type == stage_type)
    )
    stage = result.scalar_one()
    stage.config = data.config
    await db.flush()
    await db.refresh(stage)
    return APIResponse(data=_stage_to_response(stage))


@router.post("/projects/{project_id}/stages/{stage_type}/generate")
async def generate_candidates(
    project_id: UUID,
    stage_type: str,
    data: StageGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """异步生成候选内容"""
    api_logger = APILogger("generate_candidates")
    pipeline_logger = PipelineLogger(stage_type)
    start_time = time.time()
    
    api_logger.log_request("POST", f"/projects/{project_id}/stages/{stage_type}/generate", 
                          {"num_candidates": data.num_candidates})
    
    # 获取项目和阶段
    proj_result = await db.execute(select(Project).where(Project.id == project_id))
    project = proj_result.scalar_one()
    stage_result = await db.execute(
        select(Stage).where(Stage.project_id == project_id, Stage.stage_type == stage_type)
    )
    stage = stage_result.scalar_one()

    # 更新阶段状态为生成中
    stage.status = "generating"
    await db.flush()

    # 提交异步任务
    task = generate_candidates_task.delay(
        project_id=str(project_id),
        stage_type=stage_type,
        num_candidates=data.num_candidates,
        prompt=data.prompt or stage.prompt,
        config=data.config or stage.config,
    )
    
    duration_ms = (time.time() - start_time) * 1000
    api_logger.log_response("POST", f"/projects/{project_id}/stages/{stage_type}/generate", 200, duration_ms)
    pipeline_logger.log_stage_start(str(project_id))

    return APIResponse(data={
        "task_id": task.id,
        "status": "pending",
        "message": "生成任务已提交",
    })


@router.get("/projects/{project_id}/stages/{stage_type}/tasks/{task_id}")
async def get_generation_task_status(
    project_id: UUID,
    stage_type: str,
    task_id: str,
) -> APIResponse[dict[str, Any]]:
    """获取生成任务状态"""
    from app.celery_app import celery_app
    
    result = celery_app.AsyncResult(task_id)
    
    if result.ready():
        if result.successful():
            return APIResponse(data={
                "task_id": task_id,
                "status": "success",
                "result": result.result,
            })
        else:
            return APIResponse(data={
                "task_id": task_id,
                "status": "error",
                "error": str(result.result),
            })
    else:
        return APIResponse(data={
            "task_id": task_id,
            "status": "pending",
            "message": "任务正在执行中",
        })


@router.get("/projects/{project_id}/stages/{stage_type}/candidates", response_model=APIResponse[list[CandidateResponse]])
async def list_candidates(
    project_id: UUID,
    stage_type: str,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[list[CandidateResponse]]:
    stage_result = await db.execute(
        select(Stage).where(Stage.project_id == project_id, Stage.stage_type == stage_type)
    )
    stage = stage_result.scalar_one()
    result = await db.execute(
        select(Candidate)
        .where(Candidate.stage_id == stage.id)
        .order_by(Candidate.created_at)
        .options(selectinload(Candidate.artifacts))
    )
    candidates = list(result.scalars().all())
    return APIResponse(data=[_candidate_to_response(c, stage_type) for c in candidates])


@router.get("/projects/{project_id}/stages/{stage_type}/candidates/{candidate_id}", response_model=APIResponse[CandidateResponse])
async def get_candidate_detail(
    project_id: UUID,
    stage_type: str,
    candidate_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[CandidateResponse]:
    stage_result = await db.execute(
        select(Stage).where(Stage.project_id == project_id, Stage.stage_type == stage_type)
    )
    stage = stage_result.scalar_one()
    
    result = await db.execute(
        select(Candidate)
        .where(
            Candidate.id == candidate_id,
            Candidate.stage_id == stage.id
        )
        .options(selectinload(Candidate.artifacts))
    )
    candidate = result.scalar_one_or_none()
    
    if candidate is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return APIResponse(data=_candidate_to_response(candidate, stage_type))


@router.post("/projects/{project_id}/stages/{stage_type}/select", response_model=APIResponse[StageResponse])
async def select_candidate(
    project_id: UUID,
    stage_type: str,
    data: CandidateSelectRequest,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[StageResponse]:
    stage_result = await db.execute(
        select(Stage).where(Stage.project_id == project_id, Stage.stage_type == stage_type)
    )
    stage = stage_result.scalar_one()
    stage.current_candidate_id = UUID(data.candidate_id)
    await db.flush()
    await db.refresh(stage)
    return APIResponse(data=_stage_to_response(stage))


@router.post("/projects/{project_id}/stages/{stage_type}/review", response_model=APIResponse[StageResponse])
async def review_stage(
    project_id: UUID,
    stage_type: str,
    data: ReviewRequest,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[StageResponse]:
    api_logger = APILogger("review_stage")
    pipeline_logger = PipelineLogger(stage_type)
    start_time = time.time()
    
    api_logger.log_request("POST", f"/projects/{project_id}/stages/{stage_type}/review", 
                          {"action": data.action, "candidate_id": data.candidate_id})
    
    stage_result = await db.execute(
        select(Stage).where(Stage.project_id == project_id, Stage.stage_type == stage_type)
    )
    stage = stage_result.scalar_one()
    updated_stage = await review_service.handle_review(
        db=db, stage=stage, action=data.action,
        candidate_id=UUID(data.candidate_id) if data.candidate_id else None,
        comment=data.comment or "",
    )
    await db.refresh(updated_stage)
    
    duration_ms = (time.time() - start_time) * 1000
    api_logger.log_response("POST", f"/projects/{project_id}/stages/{stage_type}/review", 200, duration_ms)
    
    if data.candidate_id:
        approved = data.action == "approve"
        pipeline_logger.log_approval_action(str(project_id), data.candidate_id, approved)
    
    return APIResponse(data=_stage_to_response(updated_stage))


@router.post("/projects/{project_id}/stages/{stage_type}/rollback", response_model=APIResponse[RollbackResponse])
async def rollback_stage(
    project_id: UUID,
    stage_type: str,
    data: RollbackRequest,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[RollbackResponse]:
    from app.pipeline.engine import pipeline_engine
    affected = await pipeline_engine.rollback(db, project_id, data.target_stage)
    return APIResponse(data=RollbackResponse(
        affected_stages=affected,
        message=f"已回退到 {data.target_stage.value}，重置了 {len(affected)} 个阶段",
    ))


@router.post("/projects/{project_id}/stages/{stage_type}/recover")
async def recover_stage(
    project_id: UUID,
    stage_type: str,
    target_status: str = "ready",
    db: AsyncSession = Depends(get_db),
) -> APIResponse[dict[str, Any]]:
    """
    手动恢复阶段状态
    用于处理因中断导致的异常状态（如一直停留在"生成中"）
    
    Args:
        project_id: 项目ID
        stage_type: 阶段类型
        target_status: 目标状态 (ready/review)，默认为ready
    
    Returns:
        恢复结果
    """
    from app.utils.state_recovery import StateRecovery
    from app.schemas.enums import StageStatus
    from app.logging_config import get_logger
    
    logger = get_logger(__name__)
    
    # 验证目标状态
    valid_statuses = [StageStatus.READY.value, StageStatus.REVIEW.value]
    if target_status not in valid_statuses:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail=f"无效的目标状态，必须是: {', '.join(valid_statuses)}"
        )
    
    # 获取当前阶段状态
    stage_result = await db.execute(
        select(Stage).where(Stage.project_id == project_id, Stage.stage_type == stage_type)
    )
    stage = stage_result.scalar_one_or_none()
    
    if not stage:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail="未找到指定的阶段"
        )
    
    current_status = stage.status
    target_status_enum = StageStatus.REVIEW if target_status == "review" else StageStatus.READY
    
    logger.warning(
        f"手动恢复阶段状态 - 项目: {project_id}, "
        f"阶段: {stage_type}, 当前状态: {current_status}, 目标状态: {target_status}"
    )
    
    # 执行恢复
    success = await StateRecovery.recover_stage_by_id(
        project_id=project_id,
        stage_type=stage_type,
        target_status=target_status_enum
    )
    
    if success:
        # 刷新阶段数据
        await db.refresh(stage)
        
        return APIResponse(data={
            "success": True,
            "message": f"阶段状态已从 {current_status} 恢复到 {target_status}",
            "previous_status": current_status,
            "new_status": stage.status,
        })
    else:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail="恢复阶段状态失败"
        )


@router.get("/admin/stages/stuck")
async def get_stuck_stages() -> APIResponse[dict[str, Any]]:
    """
    获取所有卡住的阶段（管理员接口）
    返回处于"生成中"状态超过阈值的阶段
    """
    from app.utils.state_recovery import StateRecovery
    
    stuck_stages = await StateRecovery.get_stuck_stages()
    
    return APIResponse(data={
        "count": len(stuck_stages),
        "stages": stuck_stages,
        "timeout_minutes": StateRecovery.GENERATING_TIMEOUT_MINUTES,
    })


@router.post("/admin/stages/recover-all")
async def recover_all_stuck_stages() -> APIResponse[dict[str, Any]]:
    """
    自动恢复所有卡住的阶段（管理员接口）
    """
    from app.utils.state_recovery import StateRecovery
    
    stats = await StateRecovery.check_and_recover_stuck_stages()
    
    return APIResponse(data={
        "message": "状态恢复完成",
        "statistics": stats,
    })


@router.get("/projects/{project_id}/stages/{stage_type}/versions", response_model=APIResponse[list[VersionResponse]])
async def list_versions(
    project_id: UUID,
    stage_type: str,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[list[VersionResponse]]:
    stage_result = await db.execute(
        select(Stage).where(Stage.project_id == project_id, Stage.stage_type == stage_type)
    )
    stage = stage_result.scalar_one()
    versions = await version_service.get_versions(db, stage.id)
    return APIResponse(data=[
        VersionResponse(
            id=str(v.id), stage_id=str(v.stage_id),
            version_number=v.version_number,
            content_snapshot=v.content_snapshot or {},
            prompt_snapshot=v.prompt_snapshot,
            diff_summary=v.diff_summary,
            created_at=v.created_at, created_by=v.created_by,
        ) for v in versions
    ])