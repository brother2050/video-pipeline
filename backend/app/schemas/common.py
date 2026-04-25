"""
通用 Schema：APIResponse、PaginatedData、WSMessage。
"""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T | None = None
    message: str | None = None


class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class WSMessage(BaseModel):
    type: str
    data: dict[str, Any]
    timestamp: datetime
