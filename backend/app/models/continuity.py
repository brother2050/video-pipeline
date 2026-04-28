"""
角色状态机 SQLAlchemy 模型。
管理角色在多集短剧中的动态演化（服装、发型、配饰等）。
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CharacterState(Base):
    """角色状态机：记录角色在不同集数的状态变化"""

    __tablename__ = "character_states"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    character_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 集数范围
    episode_start: Mapped[int] = mapped_column(Integer, nullable=False)
    episode_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # 角色状态描述
    outfit_description: Mapped[str] = mapped_column(Text, default="")
    hairstyle: Mapped[str] = mapped_column(String(200), default="")
    accessories: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    makeup: Mapped[str] = mapped_column(String(200), default="")
    age_appearance: Mapped[str] = mapped_column(String(100), default="")
    
    # AI 生成参数
    lora_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    embedding_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reference_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # 标志性物品（必须出现的锚点）
    signature_items: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 元数据
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SceneAsset(Base):
    """场景资产库：管理可复用的场景资产"""

    __tablename__ = "scene_assets"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    scene_name: Mapped[str] = mapped_column(String(200), nullable=False)
    scene_type: Mapped[str] = mapped_column(String(50), default="interior")
    
    # 场景描述
    description: Mapped[str] = mapped_column(Text, default="")
    layout_description: Mapped[str] = mapped_column(Text, default="")
    
    # AI 生成参数
    lora_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    controlnet_depth_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    controlnet_edge_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # 时间/天气变体
    variants: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 参考图
    reference_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PacingTemplate(Base):
    """节奏模板库：存储经过验证的短剧节奏模板"""

    __tablename__ = "pacing_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    genre: Mapped[str] = mapped_column(String(100), default="")
    
    # 节奏结构
    structure: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 黄金3秒法则配置
    hook_3sec_config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 结尾钩子配置
    cliffhanger_config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 单集时长目标
    target_duration_sec: Mapped[int] = mapped_column(Integer, default=60)
    
    # 统计数据
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_completion_rate: Mapped[float] = mapped_column(default=0.0)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ConsistencyCheck(Base):
    """一致性检查记录：记录跨集一致性检测结果"""

    __tablename__ = "consistency_checks"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # 检查类型
    check_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # 检查范围
    episode_start: Mapped[int] = mapped_column(Integer, nullable=False)
    episode_end: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # 检查结果
    status: Mapped[str] = mapped_column(String(50), default="pending")
    issues_found: Mapped[int] = mapped_column(Integer, default=0)
    issues_detail: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 检查时间
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ComplianceReport(Base):
    """合规报告：记录内容合规检查结果"""

    __tablename__ = "compliance_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # 检查类型
    check_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # 检查范围
    episode_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stage_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # 检查结果
    status: Mapped[str] = mapped_column(String(50), default="pending")
    violations: Mapped[int] = mapped_column(Integer, default=0)
    violations_detail: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 检查时间
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )