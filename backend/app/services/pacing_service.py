"""
节奏控制引擎：负责短剧的叙事节奏管理，包括钩子设计、节奏模板等。
"""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.continuity import PacingTemplate
from app.models.candidate import Candidate
from app.models.project import Project


class PacingEngine:
    """节奏控制引擎"""

    async def create_pacing_template(
        self,
        db: AsyncSession,
        name: str,
        description: str = "",
        genre: str = "",
        structure: dict[str, Any] | None = None,
        hook_3sec_config: dict[str, Any] | None = None,
        cliffhanger_config: dict[str, Any] | None = None,
        target_duration_sec: int = 60,
    ) -> PacingTemplate:
        """
        创建节奏模板
        
        Args:
            db: 数据库会话
            name: 模板名称
            description: 描述
            genre: 类型
            structure: 节奏结构
            hook_3sec_config: 黄金3秒配置
            cliffhanger_config: 结尾钩子配置
            target_duration_sec: 目标时长（秒）
            
        Returns:
            创建的 PacingTemplate 对象
        """
        template = PacingTemplate(
            name=name,
            description=description,
            genre=genre,
            structure=structure or {},
            hook_3sec_config=hook_3sec_config or {},
            cliffhanger_config=cliffhanger_config or {},
            target_duration_sec=target_duration_sec,
        )
        db.add(template)
        await db.flush()
        return template

    async def get_pacing_template(
        self,
        db: AsyncSession,
        template_id: UUID,
    ) -> PacingTemplate | None:
        """
        获取节奏模板
        
        Args:
            db: 数据库会话
            template_id: 模板ID
            
        Returns:
            PacingTemplate 对象，如果不存在则返回 None
        """
        result = await db.execute(
            select(PacingTemplate).where(PacingTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def get_templates_by_genre(
        self,
        db: AsyncSession,
        genre: str,
    ) -> list[PacingTemplate]:
        """
        根据类型获取节奏模板
        
        Args:
            db: 数据库会话
            genre: 类型
            
        Returns:
            PacingTemplate 列表
        """
        result = await db.execute(
            select(PacingTemplate).where(
                PacingTemplate.genre == genre,
            ).order_by(PacingTemplate.usage_count.desc())
        )
        return list(result.scalars().all())

    async def validate_hook_3sec(
        self,
        scene_content: dict[str, Any],
        hook_config: dict[str, Any] | None = None,
    ) -> tuple[bool, str | None]:
        """
        验证是否符合黄金3秒法则
        
        Args:
            scene_content: 场景内容
            hook_config: 钩子配置
            
        Returns:
            (是否通过, 错误信息)
        """
        config = hook_config or {}
        
        # 检查是否有冲突或高潮
        action = scene_content.get("action", "")
        dialogue = scene_content.get("dialogue", [])
        
        # 检查是否有强烈的情绪或冲突
        conflict_keywords = config.get("conflict_keywords", [
            "冲突", "争吵", "打斗", "追逐", "威胁", "震惊", "意外",
            "conflict", "fight", "chase", "threat", "shock", "surprise"
        ])
        
        has_conflict = any(keyword in action for keyword in conflict_keywords)
        
        if not has_conflict and not dialogue:
            return False, "前3秒缺少冲突或高潮元素，无法抓住观众注意力"
        
        # 检查是否有悬念
        suspense_keywords = config.get("suspense_keywords", [
            "神秘", "未知", "突然", "意想不到", "谜团",
            "mystery", "unknown", "sudden", "unexpected"
        ])
        
        has_suspense = any(keyword in action for keyword in suspense_keywords)
        
        if not has_suspense:
            return False, "前3秒缺少悬念元素"
        
        return True, None

    async def validate_cliffhanger(
        self,
        scene_content: dict[str, Any],
        cliffhanger_config: dict[str, Any] | None = None,
    ) -> tuple[bool, str | None]:
        """
        验证是否符合结尾钩子要求
        
        Args:
            scene_content: 场景内容
            cliffhanger_config: 钩子配置
            
        Returns:
            (是否通过, 错误信息)
        """
        config = cliffhanger_config or {}
        
        action = scene_content.get("action", "")
        dialogue = scene_content.get("dialogue", [])
        
        # 检查是否有悬念结尾
        cliffhanger_keywords = config.get("cliffhanger_keywords", [
            "突然", "意想不到", "震惊", "悬念", "未知", "谜团",
            "门被推开", "手机响起", "震惊表情", "神秘人物",
            "sudden", "unexpected", "shock", "suspense", "mystery",
            "door opens", "phone rings", "shocked expression", "mysterious figure"
        ])
        
        has_cliffhanger = any(keyword in action for keyword in cliffhanger_keywords)
        
        if not has_cliffhanger:
            return False, "结尾缺少悬念元素，无法促使观众点击下一集"
        
        # 检查是否有未解决的问题
        if dialogue:
            last_line = dialogue[-1].get("line", "")
            question_indicators = config.get("question_indicators", ["?", "？", "什么", "谁", "为什么", "how", "what", "who", "why"])
            
            has_question = any(indicator in last_line for indicator in question_indicators)
            
            if not has_question:
                return False, "结尾缺少未解决的问题或疑问"
        
        return True, None

    async def validate_pacing(
        self,
        episode_content: dict[str, Any],
        template: PacingTemplate,
    ) -> tuple[bool, list[str]]:
        """
        根据节奏模板验证单集节奏
        
        Args:
            episode_content: 集内容
            template: 节奏模板
            
        Returns:
            (是否通过, 错误信息列表)
        """
        errors = []
        structure = template.structure
        
        scenes = episode_content.get("scenes", [])
        
        # 验证结构
        if "sections" in structure:
            sections = structure["sections"]
            
            for section in sections:
                section_type = section.get("type")
                expected_duration = section.get("duration_sec", 0)
                
                # 计算该部分的实际时长
                section_scenes = [
                    s for s in scenes
                    if s.get("section_type") == section_type
                ]
                
                actual_duration = sum(
                    s.get("duration_sec", 0) for s in section_scenes
                )
                
                # 允许10%的误差
                tolerance = expected_duration * 0.1
                if abs(actual_duration - expected_duration) > tolerance:
                    errors.append(
                        f"{section_type} 部分时长不符合预期: "
                        f"期望 {expected_duration}s, 实际 {actual_duration}s"
                    )
        
        # 验证总时长
        total_duration = sum(s.get("duration_sec", 0) for s in scenes)
        target_duration = template.target_duration_sec
        
        if abs(total_duration - target_duration) > target_duration * 0.15:
            errors.append(
                f"总时长不符合预期: "
                f"期望 {target_duration}s, 实际 {total_duration}s"
            )
        
        # 验证黄金3秒
        if scenes:
            first_scene = scenes[0]
            hook_passed, hook_error = await self.validate_hook_3sec(
                first_scene,
                template.hook_3sec_config,
            )
            if not hook_passed:
                errors.append(f"黄金3秒检查失败: {hook_error}")
        
        # 验证结尾钩子
        if scenes:
            last_scene = scenes[-1]
            cliffhanger_passed, cliffhanger_error = await self.validate_cliffhanger(
                last_scene,
                template.cliffhanger_config,
            )
            if not cliffhanger_passed:
                errors.append(f"结尾钩子检查失败: {cliffhanger_error}")
        
        return len(errors) == 0, errors

    def build_pacing_prompt(
        self,
        template: PacingTemplate,
        episode_number: int,
    ) -> str:
        """
        根据节奏模板构建生成提示词
        
        Args:
            template: 节奏模板
            episode_number: 集数
            
        Returns:
            生成提示词
        """
        prompt_parts = [
            f"请为第 {episode_number} 集生成剧本，遵循以下节奏结构：",
        ]
        
        structure = template.structure
        
        if "sections" in structure:
            for section in structure["sections"]:
                section_type = section.get("type")
                duration = section.get("duration_sec", 0)
                description = section.get("description", "")
                
                prompt_parts.append(
                    f"- {section_type}: {duration}秒, {description}"
                )
        
        if template.hook_3sec_config:
            prompt_parts.append(
                "\n重要：开头前3秒必须包含强烈的冲突或悬念元素，"
                "直接切入高潮画面，禁止冗长的空镜铺垫。"
            )
        
        if template.cliffhanger_config:
            prompt_parts.append(
                "\n重要：结尾必须停在悬念处（如：门被推开、手机响起、主角震惊表情），"
                "强迫用户点击下一集。"
            )
        
        prompt_parts.append(
            f"\n目标总时长：{template.target_duration_sec}秒"
        )
        
        return "\n".join(prompt_parts)


# 全局单例
pacing_engine = PacingEngine()