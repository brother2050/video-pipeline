"""
版本快照服务。
"""

from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stage import Stage
from app.models.version import Version


async def create_version_snapshot(
    db: AsyncSession,
    stage: Stage,
    created_by: str = "user",
) -> Version:
    """在阶段状态变更前创建版本快照"""
    # 获取当前最大版本号
    result = await db.execute(
        select(func.max(Version.version_number)).where(Version.stage_id == stage.id)
    )
    max_version = result.scalar() or 0

    version = Version(
        stage_id=stage.id,
        version_number=max_version + 1,
        content_snapshot={},
        prompt_snapshot=stage.prompt,
        created_by=created_by,
    )
    db.add(version)
    await db.flush()
    return version


async def get_versions(
    db: AsyncSession,
    stage_id: UUID,
) -> list[Version]:
    """获取阶段的所有版本历史"""
    result = await db.execute(
        select(Version).where(Version.stage_id == stage_id).order_by(Version.version_number.desc())
    )
    return list(result.scalars().all())
