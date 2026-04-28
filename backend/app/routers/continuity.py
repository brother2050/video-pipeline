"""
连续性管理路由：提供角色状态、场景资产、一致性检查等API。
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.continuity import CharacterState, SceneAsset, ConsistencyCheck
from app.schemas.continuity import (
    CharacterStateCreate,
    CharacterStateResponse,
    SceneAssetCreate,
    SceneAssetResponse,
    ConsistencyCheckResponse,
)
from app.services.continuity_service import consistency_manager

router = APIRouter(prefix="/continuity", tags=["continuity"])


@router.post("/characters/states", response_model=CharacterStateResponse)
async def create_character_state(
    state_data: CharacterStateCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建角色状态记录"""
    state = await consistency_manager.create_character_state(
        db=db,
        project_id=state_data.project_id,
        character_name=state_data.character_name,
        episode_start=state_data.episode_start,
        episode_end=state_data.episode_end,
        outfit_description=state_data.outfit_description,
        hairstyle=state_data.hairstyle,
        accessories=state_data.accessories,
        makeup=state_data.makeup,
        age_appearance=state_data.age_appearance,
        lora_path=state_data.lora_path,
        embedding_path=state_data.embedding_path,
        reference_image_path=state_data.reference_image_path,
        signature_items=state_data.signature_items,
        notes=state_data.notes,
    )
    await db.commit()
    await db.refresh(state)
    return state


@router.get("/characters/states/{project_id}/{character_name}/{episode_number}", response_model=CharacterStateResponse)
async def get_character_state(
    project_id: UUID,
    character_name: str,
    episode_number: int,
    db: AsyncSession = Depends(get_db),
):
    """获取指定角色在指定集数的状态"""
    state = await consistency_manager.get_character_state(
        db=db,
        project_id=project_id,
        character_name=character_name,
        episode_number=episode_number,
    )
    if not state:
        raise HTTPException(status_code=404, detail="Character state not found")
    return state


@router.post("/scenes/assets", response_model=SceneAssetResponse)
async def create_scene_asset(
    asset_data: SceneAssetCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建场景资产记录"""
    asset = await consistency_manager.create_scene_asset(
        db=db,
        project_id=asset_data.project_id,
        scene_name=asset_data.scene_name,
        scene_type=asset_data.scene_type,
        description=asset_data.description,
        layout_description=asset_data.layout_description,
        lora_path=asset_data.lora_path,
        controlnet_depth_path=asset_data.controlnet_depth_path,
        controlnet_edge_path=asset_data.controlnet_edge_path,
        variants=asset_data.variants,
        reference_image_path=asset_data.reference_image_path,
    )
    await db.commit()
    await db.refresh(asset)
    return asset


@router.get("/scenes/assets/{project_id}/{scene_name}", response_model=SceneAssetResponse)
async def get_scene_asset(
    project_id: UUID,
    scene_name: str,
    db: AsyncSession = Depends(get_db),
):
    """获取指定场景的资产"""
    asset = await consistency_manager.get_scene_asset(
        db=db,
        project_id=project_id,
        scene_name=scene_name,
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Scene asset not found")
    return asset


@router.post("/checks/character", response_model=ConsistencyCheckResponse)
async def check_character_consistency(
    project_id: UUID,
    episode_start: int,
    episode_end: int,
    db: AsyncSession = Depends(get_db),
):
    """检查角色一致性"""
    check = await consistency_manager.check_character_consistency(
        db=db,
        project_id=project_id,
        episode_start=episode_start,
        episode_end=episode_end,
    )
    await db.commit()
    await db.refresh(check)
    return check


@router.post("/checks/scene", response_model=ConsistencyCheckResponse)
async def check_scene_consistency(
    project_id: UUID,
    episode_start: int,
    episode_end: int,
    db: AsyncSession = Depends(get_db),
):
    """检查场景一致性"""
    check = await consistency_manager.check_scene_consistency(
        db=db,
        project_id=project_id,
        episode_start=episode_start,
        episode_end=episode_end,
    )
    await db.commit()
    await db.refresh(check)
    return check


@router.get("/prompts/character")
async def build_character_prompt(
    project_id: UUID,
    character_name: str,
    episode_number: int,
    base_prompt: str,
    db: AsyncSession = Depends(get_db),
):
    """根据角色状态构建生成提示词"""
    state = await consistency_manager.get_character_state(
        db=db,
        project_id=project_id,
        character_name=character_name,
        episode_number=episode_number,
    )
    if not state:
        raise HTTPException(status_code=404, detail="Character state not found")
    
    prompt = consistency_manager.build_character_prompt(
        character_state=state,
        base_prompt=base_prompt,
    )
    return {"prompt": prompt}


@router.get("/prompts/scene")
async def build_scene_prompt(
    project_id: UUID,
    scene_name: str,
    variant_key: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """根据场景资产构建生成提示词"""
    asset = await consistency_manager.get_scene_asset(
        db=db,
        project_id=project_id,
        scene_name=scene_name,
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Scene asset not found")
    
    prompt = consistency_manager.build_scene_prompt(
        scene_asset=asset,
        variant_key=variant_key,
    )
    return {"prompt": prompt}