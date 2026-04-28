"""
合规检查器：负责内容合规性检查，包括人脸规避、版权检查、内容审核等。
"""

import re
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.continuity import ComplianceReport


class ComplianceChecker:
    """合规检查器"""

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
        content: dict[str, Any],
    ) -> ComplianceReport:
        """
        检查人脸合规性
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            content: 内容字典
            
        Returns:
            ComplianceReport 对象
        """
        report = ComplianceReport(
            project_id=project_id,
            check_type="face",
            status="completed",
            violations=0,
            violations_detail={},
        )
        
        violations = []
        
        # 检查角色描述中是否包含禁止的人脸
        if "characters" in content:
            for character in content["characters"]:
                name = character.get("name", "")
                description = character.get("description", "")
                appearance = character.get("appearance", "")
                
                # 检查是否使用真实名人
                for forbidden in self.FORBIDDEN_FACES:
                    if forbidden in description.lower() or forbidden in appearance.lower():
                        violations.append({
                            "type": "forbidden_face",
                            "character": name,
                            "message": f"角色 {name} 的描述中包含禁止使用的人脸类型: {forbidden}",
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
        content: dict[str, Any],
    ) -> ComplianceReport:
        """
        检查音乐版权合规性
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            content: 内容字典
            
        Returns:
            ComplianceReport 对象
        """
        report = ComplianceReport(
            project_id=project_id,
            check_type="music",
            status="completed",
            violations=0,
            violations_detail={},
        )
        
        violations = []
        
        # 检查音乐计划
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
        content: dict[str, Any],
    ) -> ComplianceReport:
        """
        检查内容合规性（敏感词、暴力、色情等）
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            content: 内容字典
            
        Returns:
            ComplianceReport 对象
        """
        report = ComplianceReport(
            project_id=project_id,
            check_type="content",
            status="completed",
            violations=0,
            violations_detail={},
        )
        
        violations = []
        
        # 将内容转换为文本进行检查
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

    async def check_all_compliance(
        self,
        db: AsyncSession,
        project_id: UUID,
        content: dict[str, Any],
        episode_number: int | None = None,
        stage_type: str | None = None,
    ) -> list[ComplianceReport]:
        """
        执行所有合规检查
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            content: 内容字典
            episode_number: 集数
            stage_type: 阶段类型
            
        Returns:
            ComplianceReport 列表
        """
        reports = []
        
        # 人脸合规检查
        face_report = await self.check_face_compliance(db, project_id, content)
        face_report.episode_number = episode_number
        face_report.stage_type = stage_type
        reports.append(face_report)
        
        # 音乐版权检查
        music_report = await self.check_music_compliance(db, project_id, content)
        music_report.episode_number = episode_number
        music_report.stage_type = stage_type
        reports.append(music_report)
        
        # 内容合规检查
        content_report = await self.check_content_compliance(db, project_id, content)
        content_report.episode_number = episode_number
        content_report.stage_type = stage_type
        reports.append(content_report)
        
        return reports

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

    def generate_compliance_prompt(self) -> str:
        """
        生成合规性提示词，用于指导 LLM 生成合规内容
        
        Returns:
            合规性提示词
        """
        prompt_parts = [
            "请确保生成的内容符合以下合规要求：",
            "",
            "1. 人脸合规：",
            "   - 严禁使用真实明星、政治人物的脸进行训练或生成",
            "   - 使用 AI 生成的原创脸，并保留生成记录作为版权证明",
            "",
            "2. 音乐版权：",
            "   - BGM 必须使用免版税库或自行生成（如 Suno/Udio 商用授权）",
            "   - 切勿直接使用流行歌曲",
            "",
            "3. 内容红线：",
            "   - 避免暴力、血腥、虐待等过度暴力内容",
            "   - 避免色情、淫秽等成人内容",
            "   - 避免迷信、邪教等不良内容",
            "   - 避免政治敏感内容",
            "",
            "4. 版权保护：",
            "   - 确保所有生成内容为原创",
            "   - 避免直接复制或模仿受版权保护的作品",
        ]
        
        return "\n".join(prompt_parts)


# 全局单例
compliance_checker = ComplianceChecker()