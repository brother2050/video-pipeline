"""
路由注册。
在 main.py 中调用 register_routers(app) 注册所有路由。
"""

from fastapi import FastAPI

from app.routers.projects import router as projects_router
from app.routers.stages import router as stages_router
from app.routers.files import router as files_router
from app.routers.system import router as system_router


def register_business_routers(app: FastAPI) -> None:
    """注册 Agent 2 负责的所有路由"""
    app.include_router(projects_router, prefix="/api", tags=["projects"])
    app.include_router(stages_router, prefix="/api", tags=["stages"])
    app.include_router(files_router, prefix="/api", tags=["files"])
    app.include_router(system_router, prefix="/api", tags=["system"])
