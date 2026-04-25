"""
系统路由。
"""

import time

from fastapi import APIRouter
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database import get_db
from app.models.project import Project
from app.models.node import Node
from app.schemas.common import APIResponse
from app.schemas.system import SystemStatus

router = APIRouter()

_start_time = time.monotonic()


@router.get("/system/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/system/status", response_model=APIResponse[SystemStatus])
async def system_status(
    db: AsyncSession = Depends(get_db),
) -> APIResponse[SystemStatus]:
    total_projects = (await db.execute(select(func.count(Project.id)))).scalar() or 0
    active_projects = (await db.execute(
        select(func.count(Project.id)).where(Project.status == "active")
    )).scalar() or 0
    total_nodes = (await db.execute(select(func.count(Node.id)))).scalar() or 0
    online_nodes = (await db.execute(
        select(func.count(Node.id)).where(Node.status == "online")
    )).scalar() or 0

    # 供应商健康状态（从 registry 获取）
    supplier_health: dict[str, str] = {}
    try:
        from app.main import app
        registry = app.state.supplier_registry
        supplier_health = registry.get_all_status()
    except Exception:
        supplier_health = {}

    return APIResponse(data=SystemStatus(
        total_projects=total_projects,
        active_projects=active_projects,
        total_nodes=total_nodes,
        online_nodes=online_nodes,
        supplier_health=supplier_health,
        uptime_seconds=time.monotonic() - _start_time,
    ))
