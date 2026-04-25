from pydantic import BaseModel
"""
Supplier configuration API routes.
"""

from typing import Any

from fastapi import APIRouter, Depends, Request, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import CapabilityConfig as CapabilityConfigModel
from app.schemas import (
    CapabilityConfigResponse, CapabilityConfigUpdate,
    SupplierTestRequest, SupplierTestResponse, APIResponse,
)
from app.schemas.enums import SupplierCapability
from app.suppliers.registry import SupplierRegistry

router = APIRouter(tags=["suppliers"])


def _get_registry(request: Request) -> SupplierRegistry:
    """Get supplier registry from app state."""
    registry: SupplierRegistry = request.app.state.supplier_registry
    return registry


def _model_to_response(config: CapabilityConfigModel) -> CapabilityConfigResponse:
    """Convert ORM CapabilityConfig to response schema."""
    from app.schemas.supplier import SupplierSlot
    suppliers = [
        SupplierSlot(**s) if isinstance(s, dict) else s
        for s in (config.suppliers or [])
    ]
    return CapabilityConfigResponse(
        capability=SupplierCapability(config.capability),
        suppliers=suppliers,
        retry_count=config.retry_count,
        timeout_seconds=config.timeout_seconds,
        local_timeout_seconds=config.local_timeout_seconds,
    )


@router.get("/suppliers", response_model=APIResponse[list[CapabilityConfigResponse]])
async def list_supplier_configs(
    db: AsyncSession = Depends(get_db),
) -> APIResponse[list[CapabilityConfigResponse]]:
    """List all supplier capability configurations."""
    stmt = select(CapabilityConfigModel)
    result = await db.execute(stmt)
    configs = list(result.scalars().all())
    return APIResponse(
        success=True,
        data=[_model_to_response(c) for c in configs],
    )


@router.get("/suppliers/{capability}", response_model=APIResponse[CapabilityConfigResponse])
async def get_supplier_config(
    capability: SupplierCapability,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[CapabilityConfigResponse]:
    """Get supplier configuration for a specific capability."""
    stmt = select(CapabilityConfigModel).where(
        CapabilityConfigModel.capability == capability.value,
    )
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if config is None:
        return APIResponse(success=False, message=f"No config for {capability.value}")
    return APIResponse(success=True, data=_model_to_response(config))


@router.put("/suppliers/{capability}", response_model=APIResponse[CapabilityConfigResponse])
async def update_supplier_config(
    capability: SupplierCapability,
    data: CapabilityConfigUpdate,
    db: AsyncSession = Depends(get_db),
    registry: SupplierRegistry = Depends(_get_registry),
) -> APIResponse[CapabilityConfigResponse]:
    """Update supplier configuration for a capability (hot-reload)."""
    stmt = select(CapabilityConfigModel).where(
        CapabilityConfigModel.capability == capability.value,
    )
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()

    if config is None:
        config = CapabilityConfigModel(
            capability=capability.value,
            suppliers=[],
            retry_count=2,
            timeout_seconds=60,
            local_timeout_seconds=300,
        )
        db.add(config)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "suppliers" and value is not None:
            setattr(config, field, [s.model_dump() if hasattr(s, "model_dump") else s for s in value])
        else:
            setattr(config, field, value)

    await db.commit()
    await db.refresh(config)

    # Hot-reload registry
    all_stmt = select(CapabilityConfigModel)
    all_result = await db.execute(all_stmt)
    all_configs = [_model_to_response(c) for c in all_result.scalars().all()]
    await registry.reload_config(all_configs)

    return APIResponse(success=True, data=_model_to_response(config))


@router.post("/suppliers/test", response_model=APIResponse[SupplierTestResponse])
async def test_supplier(
    data: SupplierTestRequest,
    registry: SupplierRegistry = Depends(_get_registry),
) -> APIResponse[SupplierTestResponse]:
    """Test a specific supplier connection."""
    result = await registry.test_supplier(data.capability, data.slot)
    return APIResponse(success=True, data=result)


# --- ComfyUI 工作流分析 ---

class WorkflowAnalysisRequest(BaseModel):
    workflow: dict[str, Any]


class WorkflowNodeInfo(BaseModel):
    id: str
    class_type: str
    text_preview: str = ""
    steps: int | None = None
    cfg: float | None = None
    sampler: str | None = None
    width: int | None = None
    height: int | None = None
    is_video: bool = False
    model: str | None = None
    image: str | None = None
    prefix: str | None = None


class WorkflowAnalysis(BaseModel):
    total_nodes: int
    positive_text_nodes: list[WorkflowNodeInfo]
    negative_text_nodes: list[WorkflowNodeInfo]
    sampler_nodes: list[WorkflowNodeInfo]
    latent_nodes: list[WorkflowNodeInfo]
    checkpoint_nodes: list[WorkflowNodeInfo]
    load_image_nodes: list[WorkflowNodeInfo]
    save_nodes: list[WorkflowNodeInfo]
    is_video_workflow: bool
    overridable_params: dict[str, bool]


@router.post("/suppliers/analyze-workflow", response_model=APIResponse[WorkflowAnalysis])
async def analyze_workflow(
    data: WorkflowAnalysisRequest,
) -> APIResponse[WorkflowAnalysis]:
    """Analyze a ComfyUI workflow JSON structure."""
    from app.suppliers.workflow_parser import WorkflowParser

    parser = WorkflowParser(data.workflow)
    info = parser.get_node_info()

    analysis = WorkflowAnalysis(
        total_nodes=info["total_nodes"],
        positive_text_nodes=[WorkflowNodeInfo(id=n["id"], class_type="CLIPTextEncode", text_preview=n.get("preview", "")) for n in info.get("positive_text_nodes", [])],
        negative_text_nodes=[WorkflowNodeInfo(id=n["id"], class_type="CLIPTextEncode", text_preview=n.get("preview", "")) for n in info.get("negative_text_nodes", [])],
        sampler_nodes=[WorkflowNodeInfo(id=n["id"], class_type="KSampler", steps=n.get("steps"), cfg=n.get("cfg")) for n in info.get("sampler_nodes", [])],
        latent_nodes=[WorkflowNodeInfo(id=n["id"], class_type="EmptyLatentImage", width=n.get("width"), height=n.get("height"), is_video=info.get("has_video_nodes", False)) for n in info.get("latent_nodes", [])],
        checkpoint_nodes=[WorkflowNodeInfo(id=n["id"], class_type="CheckpointLoaderSimple", model=n.get("model", "?")) for n in info.get("checkpoint_nodes", [])],
        load_image_nodes=[WorkflowNodeInfo(id=n["id"], class_type="LoadImage", image=n.get("image", "?")) for n in info.get("load_image_nodes", [])],
        save_nodes=[],
        is_video_workflow=info.get("has_video_nodes", False),
        overridable_params={
            "has_positive": len(info.get("positive_text_nodes", [])) > 0,
            "has_negative": len(info.get("negative_text_nodes", [])) > 0,
            "has_sampler": len(info.get("sampler_nodes", [])) > 0,
            "has_latent": len(info.get("latent_nodes", [])) > 0,
            "has_checkpoint": len(info.get("checkpoint_nodes", [])) > 0,
            "has_load_image": len(info.get("load_image_nodes", [])) > 0,
            "has_video_frames": info.get("has_video_nodes", False),
        },
    )
    return APIResponse(success=True, data=analysis)


@router.post("/suppliers/upload-workflow", response_model=APIResponse[dict[str, str]])
async def upload_workflow(
    file: UploadFile = File(...),
) -> APIResponse[dict[str, str]]:
    """Upload a ComfyUI workflow JSON file and save to config/."""
    import json
    from pathlib import Path
    from app.config import settings

    if not file.filename or not file.filename.endswith(".json"):
        return APIResponse(success=False, message="Only JSON files are accepted")

    content_bytes = await file.read()
    try:
        workflow = json.loads(content_bytes)
    except json.JSONDecodeError as e:
        return APIResponse(success=False, message=f"Invalid JSON: {e}")

    # Save to config directory
    config_dir = Path("config")
    config_dir.mkdir(parents=True, exist_ok=True)
    save_path = config_dir / file.filename
    save_path.write_bytes(content_bytes)

    return APIResponse(
        success=True,
        data={"path": str(save_path), "filename": file.filename},
    )
