"""
日志配置模块
提供统一的日志配置和工具函数
"""

import logging
import sys
from pathlib import Path
from typing import Any

from app.config import settings


def setup_logging() -> None:
    """配置日志系统"""
    log_level = logging.DEBUG if settings.debug else logging.INFO
    
    # 创建日志格式
    log_format = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(log_format)
    
    # 文件处理器
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(log_dir / "app.log", encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(log_format)
    
    # 错误日志文件
    error_handler = logging.FileHandler(log_dir / "error.log", encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # 配置第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    return logging.getLogger(name)


class AsyncLogger:
    """异步任务专用日志器"""
    
    def __init__(self, name: str):
        self.logger = get_logger(f"async.{name}")
    
    def log_task_start(self, task_id: str, task_name: str, **kwargs: Any) -> None:
        """记录任务开始"""
        self.logger.info(f"Task started - ID: {task_id}, Name: {task_name}, Params: {kwargs}")
    
    def log_task_progress(self, task_id: str, progress: int, total: int, message: str = "") -> None:
        """记录任务进度"""
        self.logger.debug(f"Task progress - ID: {task_id}, {progress}/{total}, {message}")
    
    def log_task_success(self, task_id: str, task_name: str, result: Any = None) -> None:
        """记录任务成功"""
        self.logger.info(f"Task completed - ID: {task_id}, Name: {task_name}, Result: {result}")
    
    def log_task_error(self, task_id: str, task_name: str, error: Exception) -> None:
        """记录任务错误"""
        self.logger.error(f"Task failed - ID: {task_id}, Name: {task_name}, Error: {str(error)}", exc_info=True)
    
    def log_retry(self, task_id: str, task_name: str, attempt: int, max_attempts: int, error: Exception) -> None:
        """记录重试"""
        self.logger.warning(f"Task retry - ID: {task_id}, Name: {task_name}, Attempt: {attempt}/{max_attempts}, Error: {str(error)}")


class PipelineLogger:
    """流水线专用日志器"""
    
    def __init__(self, stage_type: str):
        self.logger = get_logger(f"pipeline.{stage_type}")
        self.stage_type = stage_type
    
    def log_stage_start(self, project_id: str, candidate_id: str | None = None) -> None:
        """记录阶段开始"""
        self.logger.info(f"Stage started - Type: {self.stage_type}, Project: {project_id}, Candidate: {candidate_id}")
    
    def log_stage_progress(self, project_id: str, current: int, total: int, message: str = "") -> None:
        """记录阶段进度"""
        self.logger.debug(f"Stage progress - Type: {self.stage_type}, Project: {project_id}, {current}/{total}, {message}")
    
    def log_stage_complete(self, project_id: str, candidate_id: str | None = None, output: Any = None) -> None:
        """记录阶段完成"""
        self.logger.info(f"Stage completed - Type: {self.stage_type}, Project: {project_id}, Candidate: {candidate_id}, Output: {output}")
    
    def log_stage_error(self, project_id: str, error: Exception, candidate_id: str | None = None) -> None:
        """记录阶段错误"""
        self.logger.error(f"Stage failed - Type: {self.stage_type}, Project: {project_id}, Candidate: {candidate_id}, Error: {str(error)}", exc_info=True)
    
    def log_candidate_generation(self, project_id: str, count: int) -> None:
        """记录候选生成"""
        self.logger.info(f"Candidates generated - Type: {self.stage_type}, Project: {project_id}, Count: {count}")
    
    def log_approval_action(self, project_id: str, candidate_id: str, approved: bool) -> None:
        """记录审批操作"""
        action = "approved" if approved else "rejected"
        self.logger.info(f"Candidate {action} - Type: {self.stage_type}, Project: {project_id}, Candidate: {candidate_id}")


class APILogger:
    """API专用日志器"""
    
    def __init__(self, route: str):
        self.logger = get_logger(f"api.{route}")
    
    def log_request(self, method: str, path: str, params: dict[str, Any] | None = None) -> None:
        """记录API请求"""
        self.logger.info(f"API request - Method: {method}, Path: {path}, Params: {params}")
    
    def log_response(self, method: str, path: str, status_code: int, duration_ms: float) -> None:
        """记录API响应"""
        self.logger.info(f"API response - Method: {method}, Path: {path}, Status: {status_code}, Duration: {duration_ms:.2f}ms")
    
    def log_error(self, method: str, path: str, error: Exception) -> None:
        """记录API错误"""
        self.logger.error(f"API error - Method: {method}, Path: {path}, Error: {str(error)}", exc_info=True)


class DatabaseLogger:
    """数据库专用日志器"""
    
    def __init__(self, operation: str):
        self.logger = get_logger(f"database.{operation}")
    
    def log_query(self, query: str, params: dict[str, Any] | None = None) -> None:
        """记录数据库查询"""
        self.logger.debug(f"Database query - Operation: {query}, Params: {params}")
    
    def log_transaction(self, operation: str, success: bool, duration_ms: float) -> None:
        """记录数据库事务"""
        status = "success" if success else "failed"
        self.logger.debug(f"Database transaction - Operation: {operation}, Status: {status}, Duration: {duration_ms:.2f}ms")
    
    def log_error(self, operation: str, error: Exception) -> None:
        """记录数据库错误"""
        self.logger.error(f"Database error - Operation: {operation}, Error: {str(error)}", exc_info=True)