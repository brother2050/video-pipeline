"""
阶段基类。所有 9 个阶段继承此类。
"""

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.stage import Stage
from app.models.candidate import Candidate
from app.schemas.enums import StageType


class BaseStage(ABC):
    """阶段基类"""

    stage_type: StageType

    @abstractmethod
    async def generate(
        self,
        db: AsyncSession,
        stage: Stage,
        project: Project,
        prompt: str,
        config: dict[str, Any],
        num_candidates: int,
        registry: "SupplierRegistry",
    ) -> list[Candidate]:
        """
        调用供应商生成候选素材。
        返回创建的 Candidate 列表（已持久化到数据库）。
        """
        ...

    @abstractmethod
    def build_prompt(self, project: Project, previous_contents: dict[str, Any]) -> str:
        """
        根据项目信息和前置阶段输出构建提示词。
        previous_contents: 前置阶段的 content dict
        """
        ...

    @abstractmethod
    def validate_content(self, content: dict[str, Any]) -> tuple[bool, str | None]:
        """
        校验生成内容是否符合该阶段的结构要求。
        返回 (是否有效, 错误信息)
        """
        ...

    def get_json_schema(self) -> dict[str, Any] | None:
        """获取该阶段的 JSON Schema（LLM 阶段才有）"""
        from app.pipeline.json_schemas import STAGE_SCHEMAS
        return STAGE_SCHEMAS.get(self.stage_type)
