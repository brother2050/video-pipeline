"""
合规检查路由：提供人脸合规、音乐版权、内容审核等API。
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.continuity import ComplianceReportResponse
from app.services.compliance_service import compliance_checker

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.post("/check/face", response_model=ComplianceReportResponse)
async def check_face_compliance(
    project_id: UUID,
    content: dict[str, Any],
    db: AsyncSession = Depends(get_db),
):
    """检查人脸合规性"""
    report = await compliance_checker.check_face_compliance(
        db=db,
        project_id=project_id,
        content=content,
    )
    await db.commit()
    await db.refresh(report)
    return report


@router.post("/check/music", response_model=ComplianceReportResponse)
async def check_music_compliance(
    project_id: UUID,
    content: dict[str, Any],
    db: AsyncSession = Depends(get_db),
):
    """检查音乐版权合规性"""
    report = await compliance_checker.check_music_compliance(
        db=db,
        project_id=project_id,
        content=content,
    )
    await db.commit()
    await db.refresh(report)
    return report


@router.post("/check/content", response_model=ComplianceReportResponse)
async def check_content_compliance(
    project_id: UUID,
    content: dict[str, Any],
    db: AsyncSession = Depends(get_db),
):
    """检查内容合规性"""
    report = await compliance_checker.check_content_compliance(
        db=db,
        project_id=project_id,
        content=content,
    )
    await db.commit()
    await db.refresh(report)
    return report


@router.post("/check/all", response_model=list[ComplianceReportResponse])
async def check_all_compliance(
    project_id: UUID,
    content: dict[str, Any],
    episode_number: int | None = None,
    stage_type: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """执行所有合规检查"""
    reports = await compliance_checker.check_all_compliance(
        db=db,
        project_id=project_id,
        content=content,
        episode_number=episode_number,
        stage_type=stage_type,
    )
    await db.commit()
    for report in reports:
        await db.refresh(report)
    return reports


@router.get("/prompts/compliance")
async def get_compliance_prompt():
    """获取合规性提示词"""
    prompt = compliance_checker.generate_compliance_prompt()
    return {"prompt": prompt}