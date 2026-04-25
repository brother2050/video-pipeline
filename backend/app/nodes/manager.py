"""
Node CRUD manager.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Node
from app.schemas import NodeCreate, NodeUpdate, NodeResponse
from app.schemas.enums import NodeStatus, SupplierCapability
from app.exceptions import NotFoundError


class NodeManager:
    """Manages compute node CRUD operations."""

    async def create_node(self, db: AsyncSession, data: NodeCreate) -> Node:
        """Create a new compute node."""
        node = Node(
            id=uuid4(),
            name=data.name,
            host=data.host,
            port=data.port,
            capabilities=[c.value for c in data.capabilities],
            models=data.models,
            tags=data.tags,
            enabled=True,
            status=NodeStatus.OFFLINE.value,
            last_heartbeat=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(node)
        await db.commit()
        await db.refresh(node)
        return node

    async def list_nodes(
        self,
        db: AsyncSession,
        capability: str | None = None,
        status: str | None = None,
    ) -> list[Node]:
        """List nodes with optional filters."""
        stmt = select(Node)
        if capability:
            stmt = stmt.where(Node.capabilities.contains([capability]))
        if status:
            stmt = stmt.where(Node.status == status)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_node(self, db: AsyncSession, node_id: UUID) -> Node:
        """Get a node by ID."""
        stmt = select(Node).where(Node.id == node_id)
        result = await db.execute(stmt)
        node = result.scalar_one_or_none()
        if node is None:
            raise NotFoundError(f"Node {node_id} not found")
        return node

    async def update_node(self, db: AsyncSession, node_id: UUID, data: NodeUpdate) -> Node:
        """Update a node."""
        node = await self.get_node(db, node_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "capabilities" and value is not None:
                setattr(node, field, [c.value if isinstance(c, SupplierCapability) else c for c in value])
            else:
                setattr(node, field, value)
        node.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(node)
        return node

    async def delete_node(self, db: AsyncSession, node_id: UUID) -> None:
        """Delete a node."""
        node = await self.get_node(db, node_id)
        await db.delete(node)
        await db.commit()

    async def toggle_node(self, db: AsyncSession, node_id: UUID, enabled: bool) -> Node:
        """Enable or disable a node."""
        node = await self.get_node(db, node_id)
        node.enabled = enabled
        if not enabled:
            node.status = NodeStatus.OFFLINE.value
        node.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(node)
        return node
