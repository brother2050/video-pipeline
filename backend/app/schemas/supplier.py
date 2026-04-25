"""
供应商相关 Schema。
"""

from typing import Any

from pydantic import BaseModel, Field

from app.schemas.enums import SupplierCapability


class SupplierSlot(BaseModel):
    provider: str
    model: str = ""
    base_url: str | None = None
    api_key: str | None = None
    is_local: bool = False
    priority: int = Field(default=1, ge=1)
    extra_params: dict[str, Any] = {}


class CapabilityConfigResponse(BaseModel):
    capability: SupplierCapability
    suppliers: list[SupplierSlot]
    retry_count: int
    timeout_seconds: int
    local_timeout_seconds: int

    model_config = {"from_attributes": True}


class CapabilityConfigUpdate(BaseModel):
    suppliers: list[SupplierSlot] | None = None
    retry_count: int | None = None
    timeout_seconds: int | None = None
    local_timeout_seconds: int | None = None


class SupplierTestRequest(BaseModel):
    capability: SupplierCapability
    slot: SupplierSlot
    test_prompt: str = "Hello, connection test."


class SupplierTestResponse(BaseModel):
    success: bool
    latency_ms: int
    response_preview: str | None = None
    error: str | None = None
