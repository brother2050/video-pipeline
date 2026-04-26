"""
FastAPI 应用入口。
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db, close_db, async_session_factory
from app.exceptions import register_exception_handlers
from app.ws.hub import ws_hub


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    # 创建数据目录
    data_dir = Path(settings.data_dir)
    (data_dir / "projects").mkdir(parents=True, exist_ok=True)
    (data_dir / "db").mkdir(parents=True, exist_ok=True)

    # 初始化数据库
    await init_db()

    # 初始化供应商注册表
    from sqlalchemy import select
    from app.models.supplier import CapabilityConfig
    from app.schemas.supplier import CapabilityConfigResponse, SupplierSlot
    from app.suppliers.registry import SupplierRegistry

    registry = SupplierRegistry()
    async with async_session_factory() as db:
        result = await db.execute(select(CapabilityConfig))
        configs = result.scalars().all()
        if configs:
            schema_configs = [
                CapabilityConfigResponse(
                    capability=c.capability,
                    suppliers=[SupplierSlot(**s) for s in c.suppliers],
                    retry_count=c.retry_count,
                    timeout_seconds=c.timeout_seconds,
                    local_timeout_seconds=c.local_timeout_seconds,
                )
                for c in configs
            ]
            await registry.initialize(schema_configs)
    app.state.supplier_registry = registry

    # 启动 WebSocket 心跳
    await ws_hub.start_heartbeat(settings.ws_heartbeat_interval)

    # 启动节点心跳检测
    from app.nodes.heartbeat import HeartbeatManager
    heartbeat = HeartbeatManager(
        interval=settings.heartbeat_interval_seconds,
        timeout=settings.heartbeat_timeout_seconds,
    )
    await heartbeat.start()
    app.state.heartbeat_manager = heartbeat

    yield

    # 关闭
    await heartbeat.stop()
    await ws_hub.stop_heartbeat()
    await close_db()


app = FastAPI(
    title="VideoPipeline",
    description="Local distributed video production pipeline",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 异常处理器
register_exception_handlers(app)

# WebSocket 端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    conn_id = await ws_hub.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")
            if msg_type == "subscribe":
                project_id = data.get("data", {}).get("project_id", "")
                if project_id:
                    await ws_hub.subscribe(conn_id, project_id)
            elif msg_type == "unsubscribe":
                project_id = data.get("data", {}).get("project_id", "")
                if project_id:
                    await ws_hub.unsubscribe(conn_id, project_id)
            elif msg_type == "pong":
                pass  # 客户端心跳响应，无需处理
    except WebSocketDisconnect:
        pass
    finally:
        await ws_hub.disconnect(conn_id)


# 注册所有路由
from app.routers.projects import router as projects_router
from app.routers.stages import router as stages_router
from app.routers.files import router as files_router
from app.routers.system import router as system_router
from app.routers.nodes import router as nodes_router
from app.routers.suppliers import router as suppliers_router
from app.routers.constants import router as constants_router

app.include_router(projects_router, prefix="/api", tags=["projects"])
app.include_router(stages_router, prefix="/api", tags=["stages"])
app.include_router(files_router, prefix="/api", tags=["files"])
app.include_router(system_router, prefix="/api", tags=["system"])
app.include_router(nodes_router, prefix="/api", tags=["nodes"])
app.include_router(suppliers_router, prefix="/api", tags=["suppliers"])
app.include_router(constants_router, prefix="/api", tags=["constants"])

# 静态文件（放在路由之后）
app.mount(
    "/api/files",
    StaticFiles(directory=str(Path(settings.data_dir) / "projects")),
    name="files",
)