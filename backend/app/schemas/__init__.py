"""
导出所有 Schema。
"""

from app.schemas.enums import (
    FileType,
    NodeStatus,
    ReviewAction,
    StageStatus,
    StageType,
    SupplierCapability,
)
from app.schemas.common import APIResponse, PaginatedData, WSMessage
from app.schemas.project import (
    ProjectCreate,
    ProjectDetail,
    ProjectResponse,
    ProjectUpdate,
    StageSummary,
)
from app.schemas.project_setting import (
    ProjectSettingResponse,
    ProjectSettingUpdate,
)
from app.schemas.stage import (
    StageConfigUpdate,
    StageGenerateRequest,
    StagePromptUpdate,
    StageResponse,
)
from app.schemas.candidate import (
    ArtifactResponse,
    CandidateResponse,
    CandidateSelectRequest,
)
from app.schemas.node import (
    NodeCreate,
    NodeHealthResponse,
    NodeResponse,
    NodeToggleRequest,
    NodeUpdate,
)
from app.schemas.supplier import (
    CapabilityConfigResponse,
    CapabilityConfigUpdate,
    SupplierSlot,
    SupplierTestRequest,
    SupplierTestResponse,
)
from app.schemas.version import VersionResponse
from app.schemas.system import SystemStatus

__all__ = [
    # Enums
    "StageType", "StageStatus", "ReviewAction",
    "SupplierCapability", "NodeStatus", "FileType",
    # Common
    "APIResponse", "PaginatedData", "WSMessage",
    # Project
    "ProjectCreate", "ProjectUpdate", "ProjectResponse",
    "ProjectDetail", "StageSummary",
    # Project Setting
    "ProjectSettingResponse", "ProjectSettingUpdate",
    # Stage
    "StageResponse", "StageGenerateRequest",
    "StagePromptUpdate", "StageConfigUpdate",
    # Candidate
    "CandidateResponse", "ArtifactResponse", "CandidateSelectRequest",
    # Node
    "NodeCreate", "NodeUpdate", "NodeResponse",
    "NodeToggleRequest", "NodeHealthResponse",
    # Supplier
    "SupplierSlot", "CapabilityConfigResponse",
    "CapabilityConfigUpdate", "SupplierTestRequest", "SupplierTestResponse",
    # Version
    "VersionResponse",
    # System
    "SystemStatus",
]