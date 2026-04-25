"""
公共 FastAPI 依赖。
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import NotFoundError
from app.models.project import Project
from app.models.stage import Stage


# --- 分页参数 ---

class PaginationParams:
    """分页查询参数"""
    def __init__(
        self,
        page: Annotated[int, Query(ge=1)] = 1,
        page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> None:
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size


PaginationDep = Annotated[PaginationParams, Depends()]


# --- 资源存在性验证 ---

async def get_project_or_404(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Project:
    """验证项目存在，不存在抛 404"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise NotFoundError("Project", str(project_id))
    return project


async def get_stage_or_404(
    project_id: UUID,
    stage_type: str,
    db: AsyncSession = Depends(get_db),
) -> Stage:
    """验证阶段存在，不存在抛 404"""
    result = await db.execute(
        select(Stage).where(
            Stage.project_id == project_id,
            Stage.stage_type == stage_type,
        )
    )
    stage = result.scalar_one_or_none()
    if stage is None:
        raise NotFoundError("Stage", f"{project_id}/{stage_type}")
    return stage


ProjectDep = Annotated[Project, Depends(get_project_or_404)]
StageDep = Annotated[Stage, Depends(get_stage_or_404)]


# --- 节点管理器 ---

def get_node_manager() -> "NodeManager":
    """提供 NodeManager 实例"""
    from app.nodes.manager import NodeManager
    return NodeManager()


NodeManagerDep = Annotated["NodeManager", Depends(get_node_manager)]
