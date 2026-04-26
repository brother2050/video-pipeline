"""
流水线服务：协调阶段生成流程。
"""

from typing import Any, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.stage import Stage
from app.models.candidate import Candidate
from app.schemas.enums import StageType, StageStatus
from app.pipeline.stages import STAGE_IMPLEMENTATIONS
from app.pipeline.engine import pipeline_engine, STAGE_ORDER
from app.exceptions import PipelineError, ConflictError
from app.ws.hub import ws_hub
from datetime import datetime, timezone

if TYPE_CHECKING:
    from app.suppliers.registry import SupplierRegistry


async def generate_candidates(
    db: AsyncSession,
    project: Project,
    stage: Stage,
    prompt: str | None,
    config: dict[str, Any] | None,
    num_candidates: int,
    registry: "SupplierRegistry",
) -> list[Candidate]:
    """执行阶段生成"""
    # 检查是否可以开始
    stage_type = StageType(stage.stage_type)
    can_start = await pipeline_engine.can_start(db, project.id, stage_type)
    if not can_start:
        raise ConflictError(f"Cannot start stage {stage.stage_type}: prerequisite not met")

    # 更新阶段状态为 GENERATING
    stage.status = StageStatus.GENERATING.value
    if prompt is not None:
        stage.prompt = prompt
    if config is not None:
        stage.config = config
    await db.flush()

    # WebSocket 通知：状态更新为 GENERATING
    await ws_hub.broadcast_to_project(
        str(project.id),
        {
            "type": "stage_status",
            "data": {
                "project_id": str(project.id),
                "stage_type": stage.stage_type,
                "status": StageStatus.GENERATING.value,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    # 获取阶段实现
    stage_impl = STAGE_IMPLEMENTATIONS.get(stage_type)
    if stage_impl is None:
        raise PipelineError(f"No implementation for stage {stage_type.value}")

    # 构建提示词（如果未提供）
    if not stage.prompt:
        previous_contents = await _get_previous_contents(db, project, stage_type)
        stage.prompt = stage_impl.build_prompt(project, previous_contents)
        await db.flush()

    # 执行生成
    candidates = await stage_impl.generate(
        db=db,
        stage=stage,
        project=project,
        prompt=stage.prompt,
        config=stage.config,
        num_candidates=num_candidates,
        registry=registry,
    )

    # 刷新数据库会话，确保所有关系都被正确加载
    await db.flush()
    
    # 重新加载候选以确保 artifacts 关系被正确加载
    for candidate in candidates:
        await db.refresh(candidate)

    # 更新阶段状态为 REVIEW
    stage.status = StageStatus.REVIEW.value
    await db.flush()
    await db.refresh(stage)  # 确保返回前刷新 stage

    # WebSocket 通知
    await ws_hub.broadcast_to_project(
        str(project.id),
        {
            "type": "stage_update",
            "data": {
                "project_id": str(project.id),
                "stage_type": stage_type.value,
                "status": StageStatus.REVIEW.value,
                "candidate_count": len(candidates),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    return candidates


async def _get_previous_contents(
    db: AsyncSession, project: Project, current_stage: StageType
) -> dict[str, Any]:
    """收集所有前置阶段的已锁定候选内容，合并为一个 dict"""
    current_idx = STAGE_ORDER.index(current_stage)
    merged: dict[str, Any] = {}

    for stage_type in STAGE_ORDER[:current_idx]:
        stage_result = await db.execute(
            select(Stage).where(
                Stage.project_id == project.id,
                Stage.stage_type == stage_type.value,
            )
        )
        stage = stage_result.scalar_one_or_none()
        if stage and stage.current_candidate_id:
            cand_result = await db.execute(
                select(Candidate).where(Candidate.id == stage.current_candidate_id)
            )
            candidate = cand_result.scalar_one_or_none()
            if candidate:
                merged.update(candidate.content)

    return merged