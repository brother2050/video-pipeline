"""
文件存取服务。
"""

import uuid
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Artifact
from app.schemas.enums import FileType
from app.config import settings


async def save_bytes_to_file(
    db: AsyncSession,
    candidate_id: uuid.UUID,
    data: bytes,
    file_path: Path,
    file_type: FileType,
    mime_type: str,
    metadata: dict[str, str | int] | None = None,
) -> Artifact:
    """保存字节数据到文件并创建 Artifact 记录"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(data)

    relative_path = str(file_path.relative_to(Path(settings.data_dir)))

    artifact = Artifact(
        candidate_id=candidate_id,
        file_type=file_type.value,
        file_path=relative_path,
        file_size=len(data),
        mime_type=mime_type,
        metadata_=metadata or {},
    )
    db.add(artifact)
    await db.flush()
    return artifact


def get_file_full_path(relative_path: str) -> Path:
    """获取文件的完整路径"""
    return Path(settings.data_dir) / relative_path


def get_file_url(relative_path: str) -> str:
    """获取文件的访问 URL"""
    return f"/api/files/{relative_path}"
