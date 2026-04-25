"""
系统状态 Schema。
"""

from pydantic import BaseModel


class SystemStatus(BaseModel):
    total_projects: int
    active_projects: int
    total_nodes: int
    online_nodes: int
    supplier_health: dict[str, str]
    uptime_seconds: float
