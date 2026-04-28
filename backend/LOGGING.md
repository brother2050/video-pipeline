# 日志系统使用指南

## 概述

本项目已集成完整的日志系统，支持结构化日志记录，特别针对异步任务和流水线执行进行了优化。

## 日志配置

日志系统在 `app/logging_config.py` 中配置，支持以下功能：

- **多级别日志**: DEBUG, INFO, WARNING, ERROR
- **多输出目标**: 控制台、文件、错误文件
- **结构化格式**: 包含时间、模块、级别、文件位置、消息
- **自动日志轮转**: 按日期分割日志文件

## 日志文件

日志文件存储在 `logs/` 目录下：

- `app.log`: 所有日志（INFO及以上级别）
- `error.log`: 仅错误日志（ERROR级别）

## 使用方法

### 1. 基础日志记录

```python
from app.logging_config import get_logger

logger = get_logger(__name__)

logger.info("这是一条信息日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志", exc_info=True)  # 包含异常堆栈
```

### 2. 异步任务日志

异步任务使用 `AsyncLogger`：

```python
from app.logging_config import AsyncLogger

task_logger = AsyncLogger("task_name")

# 记录任务开始
task_logger.log_task_start(task_id, "task_name", param1=value1)

# 记录任务进度
task_logger.log_task_progress(task_id, current, total, "处理中...")

# 记录任务成功
task_logger.log_task_success(task_id, "task_name", result)

# 记录任务错误
task_logger.log_task_error(task_id, "task_name", exception)

# 记录重试
task_logger.log_retry(task_id, "task_name", attempt, max_attempts, exception)
```

### 3. 流水线阶段日志

流水线阶段使用 `PipelineLogger`：

```python
from app.logging_config import PipelineLogger

pipeline_logger = PipelineLogger("worldbuilding")

# 记录阶段开始
pipeline_logger.log_stage_start(project_id, candidate_id)

# 记录阶段进度
pipeline_logger.log_stage_progress(project_id, current, total, "生成中...")

# 记录阶段完成
pipeline_logger.log_stage_complete(project_id, candidate_id, output)

# 记录阶段错误
pipeline_logger.log_stage_error(project_id, exception, candidate_id)

# 记录候选生成
pipeline_logger.log_candidate_generation(project_id, count)

# 记录审批操作
pipeline_logger.log_approval_action(project_id, candidate_id, approved=True)
```

### 4. API请求日志

API路由使用 `APILogger`：

```python
from app.logging_config import APILogger
import time

api_logger = APILogger("route_name")
start_time = time.time()

# 处理请求...

duration_ms = (time.time() - start_time) * 1000
api_logger.log_request("POST", "/api/endpoint", params)
api_logger.log_response("POST", "/api/endpoint", 200, duration_ms)
```

### 5. 数据库操作日志

数据库操作使用 `DatabaseLogger`：

```python
from app.logging_config import DatabaseLogger
import time

db_logger = DatabaseLogger("operation_name")
start_time = time.time()

# 执行数据库操作...

duration_ms = (time.time() - start_time) * 1000
db_logger.log_transaction("operation_name", success=True, duration_ms=duration_ms)
```

## 已集成的日志位置

### 异步任务 (`app/tasks/pipeline_tasks.py`)
- `generate_candidates`: 候选生成任务
- `process_stage`: 阶段处理任务
- `generate_artifact`: 产物生成任务

### API路由 (`app/routers/stages.py`)
- `generate_candidates`: 候选生成API
- `review_stage`: 阶段审核API

### 流水线引擎 (`app/pipeline/gate.py`)
- `approve`: 审批通过操作
- `_execute_stage_integration`: 阶段集成操作
- `_execute_compliance_check`: 合规检查操作

### 供应商调用 (`app/spliers/registry.py`)
- `execute`: 供应商执行调用

### 应用启动 (`app/main.py`)
- 应用生命周期事件
- 数据库初始化
- 供应商注册表初始化
- 心跳服务启动/停止

## 日志级别说明

- **DEBUG**: 详细的调试信息，用于开发调试
- **INFO**: 一般信息，记录重要操作和状态变化
- **WARNING**: 警告信息，表示潜在问题
- **ERROR**: 错误信息，表示操作失败

## 日志格式

```
2026-04-28 12:34:56 - app.tasks.pipeline_tasks - INFO - [pipeline_tasks.py:45] - Task started - ID: abc123, Name: generate_candidates, Params: {'project_id': 'xyz', 'num_candidates': 3}
```

格式说明：
- 时间戳: `2026-04-28 12:34:56`
- 模块名: `app.tasks.pipeline_tasks`
- 日志级别: `INFO`
- 位置: `[pipeline_tasks.py:45]` (文件名:行号)
- 消息: 具体的日志内容

## 调试建议

1. **异步任务调试**: 查看日志中的任务ID，追踪整个任务生命周期
2. **流水线调试**: 使用PipelineLogger追踪每个阶段的执行状态
3. **供应商调试**: 查看供应商调用的重试和失败记录
4. **性能分析**: 通过日志中的时间戳和duration_ms分析性能瓶颈
5. **错误定位**: 使用exc_info=True记录完整的异常堆栈

## 注意事项

1. 不要在日志中记录敏感信息（如API密钥、密码）
2. 生产环境建议使用INFO级别，开发环境可使用DEBUG级别
3. 日志文件会自动增长，建议定期清理或配置日志轮转
4. 异步任务中的日志会自动包含任务ID，便于追踪