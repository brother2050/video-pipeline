"""
WebSocket 连接管理中心。
"""

import asyncio
from datetime import datetime, timezone
from typing import Any

from fastapi import WebSocket
from pydantic import BaseModel


class WSConnection:
    """单个 WebSocket 连接的包装"""
    def __init__(self, websocket: WebSocket) -> None:
        self.websocket = websocket
        self.subscriptions: set[str] = set()  # 订阅的 project_id 集合
        self.connected_at: datetime = datetime.now(timezone.utc)
        self._closed: bool = False

    async def send_json(self, data: dict[str, Any]) -> None:
        await self.websocket.send_json(data)

    async def close(self) -> None:
        if self._closed:  # ← 防止重复关闭
            return
        self._closed = True
        try:
            await self.websocket.close()
        except RuntimeError:
            # WebSocket 已经被 ASGI 框架关闭了，忽略
            pass


class WebSocketHub:
    """WebSocket 连接管理器"""

    def __init__(self) -> None:
        self._connections: dict[int, WSConnection] = {}
        self._lock = asyncio.Lock()
        self._heartbeat_task: asyncio.Task[None] | None = None

    async def connect(self, websocket: WebSocket) -> int:
        """接受新连接，返回连接 ID"""
        await websocket.accept()
        async with self._lock:
            conn_id = id(websocket)
            self._connections[conn_id] = WSConnection(websocket)
            return conn_id

    async def disconnect(self, conn_id: int) -> None:
        """移除连接"""
        async with self._lock:
            conn = self._connections.pop(conn_id, None)
            if conn:
                await conn.close()

    async def subscribe(self, conn_id: int, project_id: str) -> None:
        """订阅项目消息"""
        async with self._lock:
            conn = self._connections.get(conn_id)
            if conn:
                conn.subscriptions.add(project_id)

    async def unsubscribe(self, conn_id: int, project_id: str) -> None:
        """取消订阅"""
        async with self._lock:
            conn = self._connections.get(conn_id)
            if conn:
                conn.subscriptions.discard(project_id)

    async def broadcast(self, message: dict[str, Any]) -> None:
        """广播消息给所有连接"""
        dead: list[int] = []
        async with self._lock:
            for conn_id, conn in self._connections.items():
                try:
                    await conn.send_json(message)
                except Exception:
                    dead.append(conn_id)
            for conn_id in dead:
                self._connections.pop(conn_id, None)

    async def broadcast_to_project(self, project_id: str, message: dict[str, Any]) -> None:
        """广播消息给订阅了特定项目的连接"""
        dead: list[int] = []
        async with self._lock:
            for conn_id, conn in self._connections.items():
                if project_id in conn.subscriptions:
                    try:
                        await conn.send_json(message)
                    except Exception:
                        dead.append(conn_id)
            for conn_id in dead:
                self._connections.pop(conn_id, None)

    async def send_to(self, conn_id: int, message: dict[str, Any]) -> None:
        """发送消息给特定连接"""
        conn = self._connections.get(conn_id)
        if conn:
            try:
                await conn.send_json(message)
            except Exception:
                await self.disconnect(conn_id)

    async def start_heartbeat(self, interval: int = 15) -> None:
        """启动心跳保活任务"""
        async def _heartbeat_loop() -> None:
            while True:
                await asyncio.sleep(interval)
                dead: list[int] = []
                async with self._lock:
                    for conn_id, conn in self._connections.items():
                        try:
                            await conn.send_json({"type": "ping", "data": {}, "timestamp": datetime.now(timezone.utc).isoformat()})
                        except Exception:
                            dead.append(conn_id)
                    for conn_id in dead:
                        self._connections.pop(conn_id, None)

        self._heartbeat_task = asyncio.create_task(_heartbeat_loop())

    async def stop_heartbeat(self) -> None:
        """停止心跳任务"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

    @property
    def connection_count(self) -> int:
        return len(self._connections)


# 全局单例
ws_hub = WebSocketHub()
