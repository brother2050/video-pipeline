"""
节点相关 Schema。
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.enums import NodeStatus, SupplierCapability


class NodeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    host: str
    port: int = Field(ge=1, le=65535)
    capabilities: list[SupplierCapability]
    models: list[str] = []
    tags: dict[str, str] = {}


class NodeUpdate(BaseModel):
    name: str | None = None
    host: str | None = None
    port: int | None = None
    capabilities: list[SupplierCapability] | None = None
    models: list[str] | None = None
    tags: dict[str, str] | None = None


class NodeResponse(BaseModel):
    id: str
    name: str
    host: str
    port: int
    capabilities: list[SupplierCapability]
    models: list[str]
    tags: dict[str, str]
    status: NodeStatus
    last_heartbeat: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NodeToggleRequest(BaseModel):
    enabled: bool


class NodeHealthResponse(BaseModel):
    status: str
    latency_ms: int
    models_loaded: list[str]
