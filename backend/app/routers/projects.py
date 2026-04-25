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
from app.services import project_service

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
