"""
一致性管理器：负责多集短剧中角色、场景、风格的连续性管理。
"""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.continuity import (
    CharacterState,
    SceneAsset,
    ConsistencyCheck,
)
from app.models.project import Project
from app.models.candidate import Candidate


class ConsistencyManager:
    """一致性管理器"""

    async def get_character_state(
        self,
        db: AsyncSession,
        project_id: UUID,
        character_name: str,
        episode_number: int,
    ) -> CharacterState | None:
        """
        获取指定角色在指定集数的状态
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            character_name: 角色名称
            episode_number: 集数
            
        Returns:
            CharacterState 对象，如果不存在则返回 None
        """
        result = await db.execute(
            select(CharacterState).where(
                CharacterState.project_id == project_id,
                CharacterState.character_name == character_name,
                CharacterState.episode_start <= episode_number,
                (CharacterState.episode_end >= episode_number) | (CharacterState.episode_end.is_(None)),
            )
        )
        return result.scalar_one_or_none()

    async def list_character_states(
        self,
        db: AsyncSession,
        project_id: UUID,
    ) -> list[CharacterState]:
        """
        获取项目的所有角色状态
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            
        Returns:
            CharacterState 对象列表
        """
        result = await db.execute(
            select(CharacterState).where(
                CharacterState.project_id == project_id,
            ).order_by(CharacterState.character_name, CharacterState.episode_start)
        )
        return list(result.scalars().all())

    async def get_character_state_by_id(
        self,
        db: AsyncSession,
        state_id: UUID,
    ) -> CharacterState | None:
        """
        根据ID获取角色状态
        
        Args:
            db: 数据库会话
            state_id: 角色状态ID
            
        Returns:
            CharacterState 对象，如果不存在则返回 None
        """
        result = await db.execute(
            select(CharacterState).where(
                CharacterState.id == state_id,
            )
        )
        return result.scalar_one_or_none()

    async def update_character_state(
        self,
        db: AsyncSession,
        state_id: UUID,
        character_name: str,
        episode_start: int,
        episode_end: int | None = None,
        outfit_description: str = "",
        hairstyle: str = "",
        accessories: dict[str, Any] | None = None,
        makeup: str = "",
        age_appearance: str = "",
        lora_path: str | None = None,
        embedding_path: str | None = None,
        reference_image_path: str | None = None,
        signature_items: dict[str, Any] | None = None,
        notes: str = "",
    ) -> CharacterState:
        """
        更新角色状态记录
        
        Args:
            db: 数据库会话
            state_id: 角色状态ID
            character_name: 角色名称
            episode_start: 起始集数
            episode_end: 结束集数（None表示持续到最后一集）
            outfit_description: 服装描述
            hairstyle: 发型
            accessories: 配饰字典
            makeup: 妆容
            age_appearance: 年龄外观
            lora_path: LoRA模型路径
            embedding_path: Embedding路径
            reference_image_path: 参考图路径
            signature_items: 标志性物品
            notes: 备注
            
        Returns:
            更新后的 CharacterState 对象
        """
        result = await db.execute(
            select(CharacterState).where(CharacterState.id == state_id)
        )
        state = result.scalar_one_or_none()
        
        if not state:
            raise ValueError(f"Character state with id {state_id} not found")
        
        state.character_name = character_name
        state.episode_start = episode_start
        state.episode_end = episode_end
        state.outfit_description = outfit_description
        state.hairstyle = hairstyle
        state.accessories = accessories or {}
        state.makeup = makeup
        state.age_appearance = age_appearance
        state.lora_path = lora_path
        state.embedding_path = embedding_path
        state.reference_image_path = reference_image_path
        state.signature_items = signature_items or {}
        state.notes = notes
        
        await db.flush()
        return state

    async def delete_character_state(
        self,
        db: AsyncSession,
        state_id: UUID,
    ) -> None:
        """
        删除角色状态记录
        
        Args:
            db: 数据库会话
            state_id: 角色状态ID
        """
        result = await db.execute(
            select(CharacterState).where(CharacterState.id == state_id)
        )
        state = result.scalar_one_or_none()
        
        if state:
            await db.delete(state)

    async def create_character_state(
        self,
        db: AsyncSession,
        project_id: UUID,
        character_name: str,
        episode_start: int,
        episode_end: int | None = None,
        outfit_description: str = "",
        hairstyle: str = "",
        accessories: dict[str, Any] | None = None,
        makeup: str = "",
        age_appearance: str = "",
        lora_path: str | None = None,
        embedding_path: str | None = None,
        reference_image_path: str | None = None,
        signature_items: dict[str, Any] | None = None,
        notes: str = "",
    ) -> CharacterState:
        """
        创建角色状态记录
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            character_name: 角色名称
            episode_start: 起始集数
            episode_end: 结束集数（None表示持续到最后一集）
            outfit_description: 服装描述
            hairstyle: 发型
            accessories: 配饰字典
            makeup: 妆容
            age_appearance: 年龄外观
            lora_path: LoRA模型路径
            embedding_path: Embedding路径
            reference_image_path: 参考图路径
            signature_items: 标志性物品
            notes: 备注
            
        Returns:
            创建的 CharacterState 对象
        """
        character_state = CharacterState(
            project_id=project_id,
            character_name=character_name,
            episode_start=episode_start,
            episode_end=episode_end,
            outfit_description=outfit_description,
            hairstyle=hairstyle,
            accessories=accessories or {},
            makeup=makeup,
            age_appearance=age_appearance,
            lora_path=lora_path,
            embedding_path=embedding_path,
            reference_image_path=reference_image_path,
            signature_items=signature_items or {},
            notes=notes,
        )
        db.add(character_state)
        await db.flush()
        return character_state

    async def get_scene_asset(
        self,
        db: AsyncSession,
        project_id: UUID,
        scene_name: str,
    ) -> SceneAsset | None:
        """
        获取指定场景的资产
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            scene_name: 场景名称
            
        Returns:
            SceneAsset 对象，如果不存在则返回 None
        """
        result = await db.execute(
            select(SceneAsset).where(
                SceneAsset.project_id == project_id,
                SceneAsset.scene_name == scene_name,
            )
        )
        return result.scalar_one_or_none()

    async def list_scene_assets(
        self,
        db: AsyncSession,
        project_id: UUID,
    ) -> list[SceneAsset]:
        """
        获取项目的所有场景资产
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            
        Returns:
            SceneAsset 对象列表
        """
        result = await db.execute(
            select(SceneAsset).where(
                SceneAsset.project_id == project_id,
            ).order_by(SceneAsset.scene_name)
        )
        return list(result.scalars().all())

    async def get_scene_asset_by_id(
        self,
        db: AsyncSession,
        asset_id: UUID,
    ) -> SceneAsset | None:
        """
        根据ID获取场景资产
        
        Args:
            db: 数据库会话
            asset_id: 场景资产ID
            
        Returns:
            SceneAsset 对象，如果不存在则返回 None
        """
        result = await db.execute(
            select(SceneAsset).where(
                SceneAsset.id == asset_id,
            )
        )
        return result.scalar_one_or_none()

    async def update_scene_asset(
        self,
        db: AsyncSession,
        asset_id: UUID,
        scene_name: str,
        scene_type: str = "interior",
        description: str = "",
        layout_description: str = "",
        lora_path: str | None = None,
        controlnet_depth_path: str | None = None,
        controlnet_edge_path: str | None = None,
        variants: dict[str, Any] | None = None,
        reference_image_path: str | None = None,
    ) -> SceneAsset:
        """
        更新场景资产记录
        
        Args:
            db: 数据库会话
            asset_id: 场景资产ID
            scene_name: 场景名称
            scene_type: 场景类型（interior/exterior）
            description: 场景描述
            layout_description: 布局描述
            lora_path: LoRA模型路径
            controlnet_depth_path: ControlNet深度图路径
            controlnet_edge_path: ControlNet边缘图路径
            variants: 时间/天气变体
            reference_image_path: 参考图路径
            
        Returns:
            更新后的 SceneAsset 对象
        """
        result = await db.execute(
            select(SceneAsset).where(SceneAsset.id == asset_id)
        )
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise ValueError(f"Scene asset with id {asset_id} not found")
        
        asset.scene_name = scene_name
        asset.scene_type = scene_type
        asset.description = description
        asset.layout_description = layout_description
        asset.lora_path = lora_path
        asset.controlnet_depth_path = controlnet_depth_path
        asset.controlnet_edge_path = controlnet_edge_path
        asset.variants = variants or {}
        asset.reference_image_path = reference_image_path
        
        await db.flush()
        return asset

    async def delete_scene_asset(
        self,
        db: AsyncSession,
        asset_id: UUID,
    ) -> None:
        """
        删除场景资产记录
        
        Args:
            db: 数据库会话
            asset_id: 场景资产ID
        """
        result = await db.execute(
            select(SceneAsset).where(SceneAsset.id == asset_id)
        )
        asset = result.scalar_one_or_none()
        
        if asset:
            await db.delete(asset)

    async def create_scene_asset(
        self,
        db: AsyncSession,
        project_id: UUID,
        scene_name: str,
        scene_type: str = "interior",
        description: str = "",
        layout_description: str = "",
        lora_path: str | None = None,
        controlnet_depth_path: str | None = None,
        controlnet_edge_path: str | None = None,
        variants: dict[str, Any] | None = None,
        reference_image_path: str | None = None,
    ) -> SceneAsset:
        """
        创建场景资产记录
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            scene_name: 场景名称
            scene_type: 场景类型（interior/exterior）
            description: 场景描述
            layout_description: 布局描述
            lora_path: LoRA模型路径
            controlnet_depth_path: ControlNet深度图路径
            controlnet_edge_path: ControlNet边缘图路径
            variants: 时间/天气变体
            reference_image_path: 参考图路径
            
        Returns:
            创建的 SceneAsset 对象
        """
        scene_asset = SceneAsset(
            project_id=project_id,
            scene_name=scene_name,
            scene_type=scene_type,
            description=description,
            layout_description=layout_description,
            lora_path=lora_path,
            controlnet_depth_path=controlnet_depth_path,
            controlnet_edge_path=controlnet_edge_path,
            variants=variants or {},
            reference_image_path=reference_image_path,
        )
        db.add(scene_asset)
        await db.flush()
        return scene_asset

    async def check_character_consistency(
        self,
        db: AsyncSession,
        project_id: UUID,
        episode_start: int,
        episode_end: int,
    ) -> ConsistencyCheck:
        """
        检查角色一致性
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            episode_start: 起始集数
            episode_end: 结束集数
            
        Returns:
            ConsistencyCheck 对象，包含检查结果
        """
        from datetime import datetime, timezone
        
        check = ConsistencyCheck(
            project_id=project_id,
            check_type="character",
            episode_start=episode_start,
            episode_end=episode_end,
            status="completed",
            issues_found=0,
            issues_detail={},
        )
        
        # 获取所有角色状态
        result = await db.execute(
            select(CharacterState).where(
                CharacterState.project_id == project_id,
            )
        )
        character_states = list(result.scalars().all())
        
        issues = []
        
        # 检查每个角色在指定集数范围内的状态连续性
        for state in character_states:
            if state.episode_end is None:
                continue
            
            # 检查是否有时间重叠
            overlapping = await db.execute(
                select(CharacterState).where(
                    CharacterState.project_id == project_id,
                    CharacterState.character_name == state.character_name,
                    CharacterState.id != state.id,
                    CharacterState.episode_start <= state.episode_end,
                    (CharacterState.episode_end >= state.episode_start) | (CharacterState.episode_end.is_(None)),
                )
            )
            overlapping_states = list(overlapping.scalars().all())
            
            if overlapping_states:
                issues.append({
                    "character": state.character_name,
                    "type": "overlapping_states",
                    "message": f"角色 {state.character_name} 在集数 {state.episode_start}-{state.episode_end} 与其他状态重叠",
                    "overlapping_with": [s.episode_start for s in overlapping_states],
                })
        
        check.issues_found = len(issues)
        check.issues_detail = {"issues": issues}
        db.add(check)
        await db.flush()
        
        return check

    async def check_scene_consistency(
        self,
        db: AsyncSession,
        project_id: UUID,
        episode_start: int,
        episode_end: int,
    ) -> ConsistencyCheck:
        """
        检查场景一致性
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            episode_start: 起始集数
            episode_end: 结束集数
            
        Returns:
            ConsistencyCheck 对象，包含检查结果
        """
        from datetime import datetime, timezone
        
        check = ConsistencyCheck(
            project_id=project_id,
            check_type="scene",
            episode_start=episode_start,
            episode_end=episode_end,
            status="completed",
            issues_found=0,
            issues_detail={},
        )
        
        # 获取所有场景资产
        result = await db.execute(
            select(SceneAsset).where(
                SceneAsset.project_id == project_id,
            )
        )
        scene_assets = list(result.scalars().all())
        
        issues = []
        
        # 检查场景资产是否完整
        for asset in scene_assets:
            if not asset.lora_path and not asset.controlnet_depth_path:
                issues.append({
                    "scene": asset.scene_name,
                    "type": "missing_ai_assets",
                    "message": f"场景 {asset.scene_name} 缺少 LoRA 或 ControlNet 资产",
                })
        
        check.issues_found = len(issues)
        check.issues_detail = {"issues": issues}
        db.add(check)
        await db.flush()
        
        return check

    def build_character_prompt(
        self,
        character_state: CharacterState,
        base_prompt: str,
    ) -> str:
        """
        根据角色状态构建生成提示词
        
        Args:
            character_state: 角色状态对象
            base_prompt: 基础提示词
            
        Returns:
            增强后的提示词
        """
        prompt_parts = [base_prompt]
        
        if character_state.outfit_description:
            prompt_parts.append(f"wearing {character_state.outfit_description}")
        
        if character_state.hairstyle:
            prompt_parts.append(f"with {character_state.hairstyle}")
        
        if character_state.makeup:
            prompt_parts.append(f"with {character_state.makeup} makeup")
        
        if character_state.age_appearance:
            prompt_parts.append(f"appears {character_state.age_appearance}")
        
        # 添加标志性物品
        for item_name, item_desc in character_state.signature_items.items():
            prompt_parts.append(f"with {item_desc} ({item_desc})")
        
        return ", ".join(prompt_parts)

    def build_scene_prompt(
        self,
        scene_asset: SceneAsset,
        variant_key: str | None = None,
    ) -> str:
        """
        根据场景资产构建生成提示词
        
        Args:
            scene_asset: 场景资产对象
            variant_key: 变体键（如 "day", "night", "rainy"）
            
        Returns:
            增强后的提示词
        """
        prompt_parts = [scene_asset.description]
        
        if variant_key and variant_key in scene_asset.variants:
            variant = scene_asset.variants[variant_key]
            if "lighting" in variant:
                prompt_parts.append(f"{variant['lighting']} lighting")
            if "weather" in variant:
                prompt_parts.append(f"{variant['weather']} weather")
        
        return ", ".join(prompt_parts)


# 全局单例
consistency_manager = ConsistencyManager()