"""
合规检查路由：提供人脸合规、音乐版权、内容审核等API。
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.continuity import ComplianceReport
from app.tasks.compliance_tasks import (
    check_face_recognition,
    check_music_copyright,
    check_content_moderation,
)

router = APIRouter(prefix="/compliance", tags=["compliance"])


class ComplianceCheckRequest(BaseModel):
    """合规检查请求"""
    project_id: UUID
    check_type: str = "face_recognition"
    episode_number: int | None = None
    stage_type: str | None = None


class AsyncTaskResponse(BaseModel):
    """异步任务响应"""
    task_id: str
    status: str
    message: str


@router.get("/reports")
async def get_compliance_reports(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """获取项目的合规报告列表"""
    result = await db.execute(
        select(ComplianceReport).where(
            ComplianceReport.project_id == project_id
        ).order_by(ComplianceReport.checked_at.desc())
    )
    reports = result.scalars().all()
    return reports


@router.get("/reports/{report_id}")
async def get_compliance_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """获取合规报告详情"""
    result = await db.execute(
        select(ComplianceReport).where(
            ComplianceReport.id == report_id
        )
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Compliance report not found")
    return report


@router.post("/check", response_model=AsyncTaskResponse)
async def check_compliance(request: ComplianceCheckRequest):
    """统一合规检查接口（异步）"""
    task = None
    
    if request.check_type == "face_recognition":
        task = check_face_recognition.delay(
            project_id=str(request.project_id),
            episode_number=request.episode_number,
            stage_type=request.stage_type,
        )
    elif request.check_type == "music_copyright":
        task = check_music_copyright.delay(
            project_id=str(request.project_id),
            episode_number=request.episode_number,
            stage_type=request.stage_type,
        )
    elif request.check_type == "content_moderation":
        task = check_content_moderation.delay(
            project_id=str(request.project_id),
            episode_number=request.episode_number,
            stage_type=request.stage_type,
        )
    else:
        raise HTTPException(status_code=400, detail=f"不支持的检查类型: {request.check_type}")
    
    return AsyncTaskResponse(
        task_id=task.id,
        status="pending",
        message=f"{request.check_type}检查任务已提交",
    )


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """获取异步任务状态"""
    from app.celery_app import celery_app
    
    result = celery_app.AsyncResult(task_id)
    
    if result.ready():
        if result.successful():
            return {
                "task_id": task_id,
                "status": "success",
                "result": result.result,
            }
        else:
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(result.result),
            }
    else:
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "任务正在执行中",
        }