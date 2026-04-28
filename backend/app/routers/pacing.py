"""
节奏控制路由：提供节奏模板、节奏验证等API。
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.continuity import PacingTemplateCreate, PacingTemplateResponse
from app.services.pacing_service import pacing_engine

router = APIRouter(prefix="/pacing", tags=["pacing"])


@router.post("/templates", response_model=PacingTemplateResponse)
async def create_pacing_template(
    template_data: PacingTemplateCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建节奏模板"""
    template = await pacing_engine.create_pacing_template(
        db=db,
        name=template_data.name,
        description=template_data.description,
        genre=template_data.genre,
        structure=template_data.structure,
        hook_3sec_config=template_data.hook_3sec_config,
        cliffhanger_config=template_data.cliffhanger_config,
        target_duration_sec=template_data.target_duration_sec,
    )
    await db.commit()
    await db.refresh(template)
    return template


@router.get("/templates/{template_id}", response_model=PacingTemplateResponse)
async def get_pacing_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """获取节奏模板"""
    template = await pacing_engine.get_pacing_template(
        db=db,
        template_id=template_id,
    )
    if not template:
        raise HTTPException(status_code=404, detail="Pacing template not found")
    return template


@router.get("/templates/genre/{genre}", response_model=list[PacingTemplateResponse])
async def get_templates_by_genre(
    genre: str,
    db: AsyncSession = Depends(get_db),
):
    """根据类型获取节奏模板"""
    templates = await pacing_engine.get_templates_by_genre(
        db=db,
        genre=genre,
    )
    return templates


@router.post("/validate/hook-3sec")
async def validate_hook_3sec(
    scene_content: dict[str, Any],
    hook_config: dict[str, Any] | None = None,
):
    """验证是否符合黄金3秒法则"""
    passed, error = await pacing_engine.validate_hook_3sec(
        scene_content=scene_content,
        hook_config=hook_config,
    )
    return {"passed": passed, "error": error}


@router.post("/validate/cliffhanger")
async def validate_cliffhanger(
    scene_content: dict[str, Any],
    cliffhanger_config: dict[str, Any] | None = None,
):
    """验证是否符合结尾钩子要求"""
    passed, error = await pacing_engine.validate_cliffhanger(
        scene_content=scene_content,
        cliffhanger_config=cliffhanger_config,
    )
    return {"passed": passed, "error": error}


@router.post("/validate/pacing")
async def validate_pacing(
    episode_content: dict[str, Any],
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """根据节奏模板验证单集节奏"""
    template = await pacing_engine.get_pacing_template(
        db=db,
        template_id=template_id,
    )
    if not template:
        raise HTTPException(status_code=404, detail="Pacing template not found")
    
    passed, errors = await pacing_engine.validate_pacing(
        episode_content=episode_content,
        template=template,
    )
    return {"passed": passed, "errors": errors}


@router.get("/prompts/{template_id}/{episode_number}")
async def build_pacing_prompt(
    template_id: UUID,
    episode_number: int,
    db: AsyncSession = Depends(get_db),
):
    """根据节奏模板构建生成提示词"""
    template = await pacing_engine.get_pacing_template(
        db=db,
        template_id=template_id,
    )
    if not template:
        raise HTTPException(status_code=404, detail="Pacing template not found")
    
    prompt = pacing_engine.build_pacing_prompt(
        template=template,
        episode_number=episode_number,
    )
    return {"prompt": prompt}