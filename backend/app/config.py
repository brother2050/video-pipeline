"""
配置加载模块。
优先级：环境变量 > config/default.yaml 文件 > 代码默认值。
支持热重载：调用 reload() 重新读取 YAML。
"""

from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- 服务 ---
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173"]

    # --- 数据库 ---
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/videopipeline"

    # --- 存储 ---
    data_dir: str = "data"
    max_upload_size_mb: int = 500

    # --- 节点心跳 ---
    heartbeat_interval_seconds: int = 30
    heartbeat_timeout_seconds: int = 90

    # --- 供应商 ---
    default_request_timeout: int = 60
    default_local_timeout: int = 300
    default_retry_count: int = 2

    # --- WebSocket ---
    ws_heartbeat_interval: int = 15

    # --- Celery ---
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # --- ComfyUI ---
    comfyui_default_workflow_path: str = "config/comfyui_default_workflow.json"

    # --- SD WebUI ---
    sdwebui_default_params: dict[str, Any] = {}

    model_config = {"env_prefix": "VP_", "env_file": ".env"}

    @classmethod
    def load_from_yaml(cls, yaml_path: str = "config/default.yaml") -> "Settings":
        """从 YAML 文件加载配置，环境变量仍然优先"""
        path = Path(yaml_path)
        overrides: dict[str, Any] = {}
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            # 扁平化嵌套 YAML 到 Settings 字段
            server = data.get("server", {})
            overrides["host"] = server.get("host", "0.0.0.0")
            overrides["port"] = server.get("port", 8000)
            overrides["debug"] = server.get("debug", False)
            overrides["cors_origins"] = server.get("cors_origins", ["http://localhost:5173"])

            db = data.get("database", {})
            overrides["database_url"] = db.get("url", "postgresql+asyncpg://user:password@localhost:5432/videopipeline")

            storage = data.get("storage", {})
            overrides["data_dir"] = storage.get("data_dir", "data")
            overrides["max_upload_size_mb"] = storage.get("max_upload_size_mb", 500)

            hb = data.get("heartbeat", {})
            overrides["heartbeat_interval_seconds"] = hb.get("interval_seconds", 30)
            overrides["heartbeat_timeout_seconds"] = hb.get("timeout_seconds", 90)

            sup = data.get("supplier", {})
            overrides["default_request_timeout"] = sup.get("default_timeout", 60)
            overrides["default_local_timeout"] = sup.get("default_local_timeout", 300)
            overrides["default_retry_count"] = sup.get("default_retry_count", 2)

        # 创建实例，让 BaseSettings 自动加载环境变量
        # 环境变量优先级高于 YAML 配置
        return cls(**overrides)


# 全局单例
settings = Settings.load_from_yaml()


def reload_settings() -> Settings:
    """热重载配置"""
    global settings
    settings = Settings.load_from_yaml()
    return settings