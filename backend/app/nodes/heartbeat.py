"""
Heartbeat manager for compute nodes.
Periodically checks node health and broadcasts status changes via WebSocket.
"""

import asyncio
import time as _time
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.logging_config import get_logger
from app.models import Node
from app.schemas.enums import NodeStatus
from app.schemas import WSMessage
from app.ws.hub import ws_hub
from app.nodes.health import check_node_health

logger = get_logger(__name__)


class HeartbeatManager:
    """Manages periodic heartbeat checks for all compute nodes."""

    def __init__(self, interval: int = 30, timeout: int = 90) -> None:
        self._interval = interval
        self._timeout = timeout
        self._task: asyncio.Task[None] | None = None
        self._running: bool = False

    async def start(self) -> None:
        """Start the periodic heartbeat task."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._heartbeat_loop())
        logger.info(f"Heartbeat manager started - Interval: {self._interval}s, Timeout: {self._timeout}s")

    async def stop(self) -> None:
        """Stop the heartbeat task."""
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                self._task = None
                logger.info("Heartbeat manager stopped")
                return
            self._task = None

    async def _heartbeat_loop(self) -> None:
        """Main heartbeat loop."""
        logger.debug("Starting heartbeat check cycle")
        while self._running:
            try:
                await self.check_all()
            except Exception as e:
                logger.error(f"Heartbeat check failed: {e}", exc_info=True)
            await asyncio.sleep(self._interval)

    async def check_node(self, node: Node) -> str:
        """
        Check a single node's health via HTTP GET /health.
        Returns the determined NodeStatus.
        """
        logger.debug(f"Checking node health - ID: {node.id}, Name: {node.name}, Host: {node.host}:{node.port}")
        
        try:
            health = await check_node_health(node.host, node.port, timeout=self._timeout)
            if health.status == "ok":
                logger.debug(f"Node {node.name} is ONLINE")
                return NodeStatus.ONLINE.value
            elif health.status == "busy":
                logger.debug(f"Node {node.name} is BUSY")
                return NodeStatus.BUSY.value
            else:
                logger.warning(f"Node {node.name} returned ERROR status: {health.status}")
                return NodeStatus.ERROR.value
        except Exception as e:
            logger.warning(f"Node {node.name} health check failed: {e}")
            return NodeStatus.OFFLINE.value

    async def check_all(self) -> None:
        """Check all enabled nodes, broadcast status changes via WebSocket."""
        logger.debug("Starting health check for all enabled nodes")
        
        async with async_session_factory() as db:
            stmt = select(Node).where(Node.enabled == True)
            result = await db.execute(stmt)
            nodes = list(result.scalars().all())
        
        logger.info(f"Health check started for {len(nodes)} enabled nodes")
        status_changes = []

        for node in nodes:
            old_status = node.status
            new_status = await self.check_node(node)

            async with async_session_factory() as db:
                stmt = select(Node).where(Node.id == node.id)
                result = await db.execute(stmt)
                db_node = result.scalar_one_or_none()
                if db_node is None:
                    continue

                db_node.status = new_status
                if new_status == NodeStatus.ONLINE.value:
                    db_node.last_heartbeat = datetime.now(timezone.utc)
                db_node.updated_at = datetime.now(timezone.utc)
                await db.commit()

            if old_status != new_status:
                status_changes.append((node.name, old_status, new_status))
                logger.info(f"Node status changed - Name: {node.name}, Old: {old_status}, New: {new_status}")
                
                ws_message = WSMessage(
                    type="node_status_change",
                    data={
                        "node_id": str(node.id),
                        "node_name": node.name,
                        "old_status": old_status,
                        "new_status": new_status,
                    },
                    timestamp=datetime.now(timezone.utc),
                )
                await ws_hub.broadcast(ws_message.model_dump(mode="json"))
        
        if status_changes:
            logger.info(f"Health check completed - Total nodes: {len(nodes)}, Status changes: {len(status_changes)}")
        else:
            logger.debug(f"Health check completed - Total nodes: {len(nodes)}, No status changes")