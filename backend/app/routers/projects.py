"""
项目路由。
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import PaginationDep, get_project_or_404
from app.models.project import Project
from app.schemas.common import APIResponse, PaginatedData
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetail
from app.schemas.project_setting import ProjectSettingResponse, ProjectSettingUpdate
from app.services import project_service, setting_service

router = APIRouter()


@router.post("/projects", response_model=APIResponse[ProjectResponse], status_code=201)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ProjectResponse]:
    """创建新项目"""
    project = await project_service.create_project(db, data)
    resp = await project_service.build_project_response(db, project)
    return APIResponse(data=ProjectResponse(**resp))


@router.get("/projects", response_model=APIResponse[PaginatedData[ProjectResponse]])
async def list_projects(
    pagination: PaginationDep,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[PaginatedData[ProjectResponse]]:
    """分页获取项目列表"""
    projects, total = await project_service.list_projects(db, pagination.offset, pagination.page_size)
    items: list[ProjectResponse] = []
    for p in projects:
        resp = await project_service.build_project_response(db, p)
        items.append(ProjectResponse(**resp))
    return APIResponse(data=PaginatedData(
        items=items, total=total, page=pagination.page, page_size=pagination.page_size
    ))


@router.get("/projects/{project_id}", response_model=APIResponse[ProjectDetail])
async def get_project(
    project: Project = Depends(get_project_or_404),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ProjectDetail]:
    """获取项目详情"""
    resp = await project_service.build_project_response(db, project)
    return APIResponse(data=ProjectDetail(**resp))


@router.put("/projects/{project_id}", response_model=APIResponse[ProjectResponse])
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ProjectResponse]:
    """更新项目"""
    project = await project_service.update_project(db, project_id, data)
    resp = await project_service.build_project_response(db, project)
    return APIResponse(data=ProjectResponse(**resp))


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """删除项目"""
    await project_service.delete_project(db, project_id)


@router.get(
    "/projects/{project_id}/settings",
    response_model=APIResponse[ProjectSettingResponse],
)
async def get_project_settings(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ProjectSettingResponse]:
    """获取项目设置（不存在则返回默认值）"""
    settings = await setting_service.get_or_create_settings(db, project_id)
    resp = _build_setting_response(settings)
    return APIResponse(data=ProjectSettingResponse(**resp))


@router.put(
    "/projects/{project_id}/settings",
    response_model=APIResponse[ProjectSettingResponse],
)
async def update_project_settings(
    project_id: UUID,
    data: ProjectSettingUpdate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ProjectSettingResponse]:
    """更新项目设置（只传需要修改的字段）"""
    settings = await setting_service.update_settings(db, project_id, data)
    resp = _build_setting_response(settings)
    return APIResponse(data=ProjectSettingResponse(**resp))


def _build_setting_response(settings) -> dict[str, Any]:
    """构建 ProjectSettingResponse，将 UUID 转换为字符串"""
    return {
        "id": str(settings.id),
        "project_id": str(settings.project_id),
        "default_num_candidates": settings.default_num_candidates,
        "image_width": settings.image_width,
        "image_height": settings.image_height,
        "video_resolution": settings.video_resolution,
        "video_fps": settings.video_fps,
        "video_duration_sec": settings.video_duration_sec,
        "default_tts_voice": settings.default_tts_voice,
        "default_bgm_style": settings.default_bgm_style,
        "default_sfx_library": settings.default_sfx_library,
        "output_bitrate": settings.output_bitrate,
        "output_audio_codec": settings.output_audio_codec,
        "output_audio_bitrate": settings.output_audio_bitrate,
        "subtitle_enabled": settings.subtitle_enabled,
        "subtitle_font": settings.subtitle_font,
        "subtitle_size": settings.subtitle_size,
        "subtitle_color": settings.subtitle_color,
        "subtitle_position": settings.subtitle_position,
        "color_grade_lut": settings.color_grade_lut,
        "color_grade_intensity": settings.color_grade_intensity,
        "vignette_intensity": settings.vignette_intensity,
        "grain_intensity": settings.grain_intensity,
        "preferred_suppliers": settings.preferred_suppliers,
        "comfyui_workflow_path": settings.comfyui_workflow_path,
        "extra": settings.extra,
        "created_at": settings.created_at,
        "updated_at": settings.updated_at,
    }