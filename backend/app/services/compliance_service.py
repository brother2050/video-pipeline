"""
合规检查器：负责内容合规性检查，包括人脸规避、版权检查、内容审核等。
"""

import re
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.continuity import ComplianceReport, CharacterState
from app.models.candidate import Candidate
from app.models.stage import Stage


class ComplianceChecker:
    """合规检查器"""

    def __init__(self) -> None:
        """初始化合规检查器"""
        pass

    # 敏感词库
    SENSITIVE_KEYWORDS = {
        "violence": [
            "杀人", "谋杀", "血腥", "暴力", "虐待", "酷刑", "强奸", "性侵",
            "kill", "murder", "blood", "violence", "abuse", "torture", "rape",
        ],
        "politics": [
            "政治人物", "领导人", "总统", "主席", "总理", "领导人",
            "president", "chairman", "prime minister", "political figure",
        ],
        "pornography": [
            "色情", "淫秽", "裸体", "性交", "性爱", "成人内容",
            "pornography", "nude", "sex", "adult content",
        ],
        "superstition": [
            "迷信", "邪教", "占卜", "算命", "风水", "鬼神",
            "superstition", "cult", "divination", "fortune telling",
        ],
    }

    # 禁止使用的名人/政治人物名单
    FORBIDDEN_FACES = [
        "明星", "名人", "政治人物", "领导人",
        "celebrity", "politician", "political figure",
    ]

    async def check_face_compliance(
        self,
        db: AsyncSession,
        project_id: UUID,
        episode_number: int | None = None,
        stage_type: str | None = None,
    ) -> ComplianceReport:
        """
        检查人脸合规性
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            episode_number: 集数
            stage_type: 阶段类型
            
        Returns:
            ComplianceReport 对象
        """
        from app.models.continuity import CharacterState
        
        report = ComplianceReport(
            project_id=project_id,
            check_type="face",
            status="completed",
            violations=0,
            violations_detail={},
            episode_number=episode_number,
            stage_type=stage_type,
        )
        
        violations = []
        
        # 从数据库查询角色状态
        result = await db.execute(
            select(CharacterState).where(
                CharacterState.project_id == project_id
            )
        )
        characters = result.scalars().all()
        
        # 检查每个角色状态
        for character in characters:
            content = {
                "name": character.character_name,
                "description": character.outfit_description,
                "appearance": character.age_appearance,
            }
            
            # 检查是否使用真实名人
            for forbidden in self.FORBIDDEN_FACES:
                if forbidden in content["description"].lower() or forbidden in content["appearance"].lower():
                    violations.append({
                        "type": "forbidden_face",
                        "character": content["name"],
                        "message": f"角色 {content['name']} 的描述中包含禁止使用的人脸类型: {forbidden}",
                    })
        
        report.violations = len(violations)
        report.violations_detail = {"violations": violations}
        db.add(report)
        await db.flush()
        
        return report

    async def check_music_compliance(
        self,
        db: AsyncSession,
        project_id: UUID,
        episode_number: int | None = None,
        stage_type: str | None = None,
    ) -> ComplianceReport:
        """
        检查音乐版权合规性
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            episode_number: 集数
            stage_type: 阶段类型
            
        Returns:
            ComplianceReport 对象
        """
        report = ComplianceReport(
            project_id=project_id,
            check_type="music",
            status="completed",
            violations=0,
            violations_detail={},
            episode_number=episode_number,
            stage_type=stage_type,
        )
        
        violations = []
        
        # 从数据库查询候选内容（音乐相关）
        if stage_type:
            result = await db.execute(
                select(Candidate)
                .join(Stage)
                .where(Stage.stage_type == stage_type)
                .options(joinedload(Candidate.stage))
            )
            candidates = result.scalars().all()
            
            # 检查候选内容中的音乐信息
            for candidate in candidates:
                content = candidate.content or {}
                if "bgm_plan" in content:
                    for bgm in content["bgm_plan"]:
                        reference_track = bgm.get("reference_track", "")
                        
                        # 检查是否直接使用流行歌曲
                        if reference_track and not self._is_royalty_free(reference_track):
                            violations.append({
                                "type": "copyright_music",
                                "track": reference_track,
                                "message": f"参考曲目 {reference_track} 可能涉及版权问题，请使用免版税音乐",
                            })
        
        report.violations = len(violations)
        report.violations_detail = {"violations": violations}
        db.add(report)
        await db.flush()
        
        return report

    async def check_content_compliance(
        self,
        db: AsyncSession,
        project_id: UUID,
        episode_number: int | None = None,
        stage_type: str | None = None,
    ) -> ComplianceReport:
        """
        检查内容合规性（敏感词、暴力、色情等）
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            episode_number: 集数
            stage_type: 阶段类型
            
        Returns:
            ComplianceReport 对象
        """
        report = ComplianceReport(
            project_id=project_id,
            check_type="content",
            status="completed",
            violations=0,
            violations_detail={},
            episode_number=episode_number,
            stage_type=stage_type,
        )
        
        violations = []
        
        # 从数据库查询候选内容
        if stage_type:
            result = await db.execute(
                select(Candidate)
                .join(Stage)
                .where(Stage.stage_type == stage_type)
                .options(joinedload(Candidate.stage))
            )
            candidates = result.scalars().all()
            
            # 检查候选内容中的敏感词
            for candidate in candidates:
                content = candidate.content or {}
                text_content = self._extract_text(content)
                
                # 检查各类敏感词
                for category, keywords in self.SENSITIVE_KEYWORDS.items():
                    for keyword in keywords:
                        if keyword in text_content:
                            violations.append({
                                "type": category,
                                "keyword": keyword,
                                "message": f"发现敏感词 ({category}): {keyword}",
                            })
        
        report.violations = len(violations)
        report.violations_detail = {"violations": violations}
        db.add(report)
        await db.flush()
        
        return report

    def _extract_text(self, content: Any) -> str:
        """
        从内容字典中提取所有文本
        
        Args:
            content: 内容对象
            
        Returns:
            提取的文本字符串
        """
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            return " ".join(self._extract_text(v) for v in content.values())
        elif isinstance(content, list):
            return " ".join(self._extract_text(item) for item in content)
        else:
            return str(content)

    def _is_royalty_free(self, track_name: str) -> bool:
        """
        检查曲目是否为免版税音乐
        
        Args:
            track_name: 曲目名称
            
        Returns:
            是否为免版税
        """
        # 免版税音乐库标识
        royalty_free_indicators = [
            "royalty free",
            "免版税",
            "suno",
            "udio",
            "musicgen",
            "audiocraft",
            "epidemic sound",
            "artlist",
        ]
        
        track_lower = track_name.lower()
        return any(indicator in track_lower for indicator in royalty_free_indicators)