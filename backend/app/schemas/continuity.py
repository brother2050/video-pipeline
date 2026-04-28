"""
连续性管理相关 Schema。
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CharacterStateCreate(BaseModel):
    project_id: UUID
    character_name: str = Field(min_length=1, max_length=100)
    episode_start: int = Field(ge=1)
    episode_end: int | None = Field(default=None, ge=1)
    outfit_description: str = Field(default="", max_length=2000)
    hairstyle: str = Field(default="", max_length=200)
    accessories: dict[str, Any] = Field(default_factory=dict)
    makeup: str = Field(default="", max_length=200)
    age_appearance: str = Field(default="", max_length=100)
    lora_path: str | None = Field(default=None, max_length=500)
    embedding_path: str | None = Field(default=None, max_length=500)
    reference_image_path: str | None = Field(default=None, max_length=500)
    signature_items: dict[str, Any] = Field(default_factory=dict)
    notes: str = Field(default="", max_length=2000)


class CharacterStateResponse(BaseModel):
    id: UUID
    project_id: UUID
    character_name: str
    episode_start: int
    episode_end: int | None
    outfit_description: str
    hairstyle: str
    accessories: dict[str, Any]
    makeup: str
    age_appearance: str
    lora_path: str | None
    embedding_path: str | None
    reference_image_path: str | None
    signature_items: dict[str, Any]
    notes: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SceneAssetCreate(BaseModel):
    project_id: UUID
    scene_name: str = Field(min_length=1, max_length=200)
    scene_type: str = Field(default="interior", max_length=50)
    description: str = Field(default="", max_length=2000)
    layout_description: str = Field(default="", max_length=2000)
    lora_path: str | None = Field(default=None, max_length=500)
    controlnet_depth_path: str | None = Field(default=None, max_length=500)
    controlnet_edge_path: str | None = Field(default=None, max_length=500)
    variants: dict[str, Any] = Field(default_factory=dict)
    reference_image_path: str | None = Field(default=None, max_length=500)


class SceneAssetResponse(BaseModel):
    id: UUID
    project_id: UUID
    scene_name: str
    scene_type: str
    description: str
    layout_description: str
    lora_path: str | None
    controlnet_depth_path: str | None
    controlnet_edge_path: str | None
    variants: dict[str, Any]
    reference_image_path: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConsistencyCheckResponse(BaseModel):
    id: UUID
    project_id: UUID
    check_type: str
    episode_start: int
    episode_end: int
    status: str
    issues_found: int
    issues_detail: dict[str, Any]
    checked_at: datetime

    model_config = {"from_attributes": True}


class PacingTemplateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    genre: str = Field(default="", max_length=100)
    structure: dict[str, Any] = Field(default_factory=dict)
    hook_3sec_config: dict[str, Any] = Field(default_factory=dict)
    cliffhanger_config: dict[str, Any] = Field(default_factory=dict)
    target_duration_sec: int = Field(default=60, ge=10, le=600)


class PacingTemplateResponse(BaseModel):
    id: UUID
    name: str
    description: str
    genre: str
    structure: dict[str, Any]
    hook_3sec_config: dict[str, Any]
    cliffhanger_config: dict[str, Any]
    target_duration_sec: int
    usage_count: int
    avg_completion_rate: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}