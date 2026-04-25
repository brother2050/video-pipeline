"""
文件访问路由。
"""

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.candidate import Artifact
from app.schemas.common import APIResponse
from app.schemas.candidate import ArtifactResponse
from app.config import settings
from app.exceptions import NotFoundError

router = APIRouter()


@router.get("/files/{file_path:path}")
async def serve_file(file_path: str) -> FileResponse:
    """返回文件内容，自动设置 Content-Type"""
    full_path = Path(settings.data_dir) / "projects" / file_path
    if not full_path.exists():
        raise NotFoundError("File", file_path)
    return FileResponse(path=str(full_path))


@router.get("/files/{file_path:path}/info", response_model=APIResponse[ArtifactResponse])
async def file_info(
    file_path: str,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ArtifactResponse]:
    """返回文件元信息"""
    result = await db.execute(
        select(Artifact).where(Artifact.file_path == f"projects/{file_path}")
    )
    artifact = result.scalar_one_or_none()
    if artifact is None:
        raise NotFoundError("Artifact", file_path)
    return APIResponse(data=ArtifactResponse(
        id=str(artifact.id),
        candidate_id=str(artifact.candidate_id),
        file_type=artifact.file_type,
        file_path=artifact.file_path,
        file_url=f"/api/files/{file_path}",
        file_size=artifact.file_size,
        mime_type=artifact.mime_type,
        metadata=artifact.metadata_ or {},
        created_at=artifact.created_at,
    ))
