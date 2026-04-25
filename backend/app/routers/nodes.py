"""
Node management API routes.
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_node_manager
from app.nodes.manager import NodeManager
from app.nodes.health import check_node_health
from app.schemas import (
    NodeCreate, NodeUpdate, NodeResponse, NodeToggleRequest,
    NodeHealthResponse, APIResponse,
)
from app.exceptions import NotFoundError

router = APIRouter(tags=["nodes"])


def _node_to_response(node: Any) -> NodeResponse:
    """Convert ORM Node to NodeResponse schema."""
    from app.schemas.enums import NodeStatus, SupplierCapability
    return NodeResponse(
        id=str(node.id),
        name=node.name,
        host=node.host,
        port=node.port,
        capabilities=[SupplierCapability(c) for c in (node.capabilities or [])],
        models=node.models or [],
        tags=node.tags or {},
        status=NodeStatus(node.status) if node.status else NodeStatus.OFFLINE,
        last_heartbeat=node.last_heartbeat,
        created_at=node.created_at,
        updated_at=node.updated_at,
    )


@router.post("/nodes", response_model=APIResponse[NodeResponse])
async def create_node(
    data: NodeCreate,
    db: AsyncSession = Depends(get_db),
    manager: NodeManager = Depends(get_node_manager),
) -> APIResponse[NodeResponse]:
    """Create a new compute node."""
    node = await manager.create_node(db, data)
    return APIResponse(success=True, data=_node_to_response(node))


@router.get("/nodes", response_model=APIResponse[list[NodeResponse]])
async def list_nodes(
    capability: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    manager: NodeManager = Depends(get_node_manager),
) -> APIResponse[list[NodeResponse]]:
    """List all nodes with optional filters."""
    nodes = await manager.list_nodes(db, capability=capability, status=status)
    return APIResponse(success=True, data=[_node_to_response(n) for n in nodes])


@router.get("/nodes/{node_id}", response_model=APIResponse[NodeResponse])
async def get_node(
    node_id: UUID,
    db: AsyncSession = Depends(get_db),
    manager: NodeManager = Depends(get_node_manager),
) -> APIResponse[NodeResponse]:
    """Get a node by ID."""
    node = await manager.get_node(db, node_id)
    return APIResponse(success=True, data=_node_to_response(node))


@router.put("/nodes/{node_id}", response_model=APIResponse[NodeResponse])
async def update_node(
    node_id: UUID,
    data: NodeUpdate,
    db: AsyncSession = Depends(get_db),
    manager: NodeManager = Depends(get_node_manager),
) -> APIResponse[NodeResponse]:
    """Update a node."""
    node = await manager.update_node(db, node_id, data)
    return APIResponse(success=True, data=_node_to_response(node))


@router.delete("/nodes/{node_id}", response_model=APIResponse[None])
async def delete_node(
    node_id: UUID,
    db: AsyncSession = Depends(get_db),
    manager: NodeManager = Depends(get_node_manager),
) -> APIResponse[None]:
    """Delete a node."""
    await manager.delete_node(db, node_id)
    return APIResponse(success=True, data=None)


@router.post("/nodes/{node_id}/toggle", response_model=APIResponse[NodeResponse])
async def toggle_node(
    node_id: UUID,
    data: NodeToggleRequest,
    db: AsyncSession = Depends(get_db),
    manager: NodeManager = Depends(get_node_manager),
) -> APIResponse[NodeResponse]:
    """Enable or disable a node."""
    node = await manager.toggle_node(db, node_id, data.enabled)
    return APIResponse(success=True, data=_node_to_response(node))


@router.get("/nodes/{node_id}/health", response_model=APIResponse[NodeHealthResponse])
async def get_node_health(
    node_id: UUID,
    db: AsyncSession = Depends(get_db),
    manager: NodeManager = Depends(get_node_manager),
) -> APIResponse[NodeHealthResponse]:
    """Check a node's health."""
    node = await manager.get_node(db, node_id)
    health = await check_node_health(node.host, node.port)
    return APIResponse(success=True, data=health)
