"""
项目 CRUD 服务。
"""

from typing import Any
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.stage import Stage
from app.models.candidate import Candidate
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, StageSummary
from app.schemas.enums import StageType, StageStatus
from app.pipeline.engine import pipeline_engine, STAGE_ORDER
from app.services import setting_service


async def create_project(db: AsyncSession, data: ProjectCreate) -> Project:
    """创建项目并初始化 9 个阶段"""
    project = Project(
        name=data.name,
        description=data.description,
        genre=data.genre,
        target_episodes=data.target_episodes,
        target_duration_minutes=data.target_duration_minutes,
        current_stage=StageType.WORLDBUILDING.value,
        status="active",
    )
    db.add(project)
    await db.flush()

    await pipeline_engine.initialize_project(db, project)
    await db.flush()

    await setting_service.get_or_create_settings(db, project.id)
    await db.flush()

    return project


async def get_project(db: AsyncSession, project_id: UUID) -> Project:
    """获取单个项目"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one()


async def list_projects(
    db: AsyncSession, offset: int, limit: int
) -> tuple[list[Project], int]:
    """分页获取项目列表"""
    count_result = await db.execute(select(func.count(Project.id)))
    total = count_result.scalar() or 0

    result = await db.execute(
        select(Project).order_by(Project.updated_at.desc()).offset(offset).limit(limit)
    )
    projects = list(result.scalars().all())
    return projects, total


async def update_project(db: AsyncSession, project_id: UUID, data: ProjectUpdate) -> Project:
    """更新项目"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one()
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    await db.flush()
    return project


async def delete_project(db: AsyncSession, project_id: UUID) -> None:
    """删除项目"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one()
    await db.delete(project)
    await db.flush()


async def build_project_response(db: AsyncSession, project: Project) -> dict[str, Any]:
    """构建 ProjectResponse（含 stages_summary）"""
    stages_result = await db.execute(
        select(Stage).where(Stage.project_id == project.id)
    )
    stages = list(stages_result.scalars().all())

    summaries: list[StageSummary] = []
    for stage in stages:
        cand_count_result = await db.execute(
            select(func.count(Candidate.id)).where(Candidate.stage_id == stage.id)
        )
        cand_count = cand_count_result.scalar() or 0
        summaries.append(StageSummary(
            stage_type=StageType(stage.stage_type),
            status=StageStatus(stage.status),
            has_candidates=cand_count > 0,
            candidate_count=cand_count,
        ))

    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "genre": project.genre,
        "target_episodes": project.target_episodes,
        "target_duration_minutes": project.target_duration_minutes,
        "current_stage": StageType(project.current_stage),
        "status": project.status,
        "stages_summary": summaries,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }