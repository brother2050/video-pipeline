"""
项目设置服务。
创建项目时自动创建默认设置，项目删除时级联删除。
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import ProjectSetting
from app.schemas.project_setting import ProjectSettingUpdate


async def get_or_create_settings(
    db: AsyncSession,
    project_id: UUID,
) -> ProjectSetting:
    """获取项目设置，不存在则创建默认值"""
    result = await db.execute(
        select(ProjectSetting).where(ProjectSetting.project_id == project_id)
    )
    settings = result.scalar_one_or_none()
    if settings is None:
        settings = ProjectSetting(project_id=project_id)
        db.add(settings)
        await db.flush()
        await db.refresh(settings)
    return settings


async def update_settings(
    db: AsyncSession,
    project_id: UUID,
    data: ProjectSettingUpdate,
) -> ProjectSetting:
    """更新项目设置"""
    settings = await get_or_create_settings(db, project_id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)
    await db.flush()
    await db.refresh(settings)
    return settings