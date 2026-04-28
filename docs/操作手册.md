# VideoPipeline 操作手册

## 📋 文档信息

| 项目 | 内容 |
|------|------|
| 项目名称 | VideoPipeline |
| 版本 | 1.0.0 |
| 最后更新 | 2026-04-28 |
| 文档状态 | 完整版 |

---

## 目录

1. [快速开始](#1-快速开始)
2. [安装部署](#2-安装部署)
3. [基础操作](#3-基础操作)
4. [流水线管理](#4-流水线管理)
5. [供应商管理](#5-供应商管理)
6. [节点管理](#6-节点管理)
7. [连续性管理](#7-连续性管理)
8. [节奏管理](#8-节奏管理)
9. [合规检查](#9-合规检查)
10. [故障排除](#10-故障排除)
11. [最佳实践](#11-最佳实践)

---

## 1. 快速开始

### 1.1 系统要求

**最低配置**：
- CPU: 4 核
- 内存: 8GB
- 存储: 100GB SSD
- 操作系统: Linux / macOS / Windows

**推荐配置**：
- CPU: 8 核
- 内存: 16GB
- 存储: 500GB SSD
- 操作系统: Linux / macOS / Windows
- GPU: NVIDIA RTX 3060 或更高（用于本地图像/视频生成）

### 1.2 依赖软件

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- FFmpeg 4+
- Node.js 18+

### 1.3 5 分钟快速启动

#### 步骤 1: 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd video-pipeline

# 安装后端依赖
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 安装前端依赖
cd ../frontend
npm install
```

#### 步骤 2: 配置数据库

```bash
# 启动 PostgreSQL
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql

# 创建数据库
createdb videopipeline
```

#### 步骤 3: 配置 Redis

```bash
# 启动 Redis
# macOS
brew services start redis

# Linux
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:latest
```

#### 步骤 4: 配置环境变量

在 `backend/.env` 中添加：

```bash
VP_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/videopipeline
VP_CELERY_BROKER_URL=redis://localhost:6379/0
VP_CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

#### 步骤 5: 初始化数据库

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
```

#### 步骤 6: 启动服务

```bash
# 一键启动所有服务
cd backend
chmod +x start_all_services.sh
./start_all_services.sh

# 启动前端
cd ../frontend
npm run dev
```

#### 步骤 7: 访问系统

- **前端界面**: http://localhost:5173
- **API 文档**: http://localhost:8000/docs
- **Flower 监控**: http://localhost:5555

---

## 2. 安装部署

### 2.1 后端安装

#### 2.1.1 创建虚拟环境

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

#### 2.1.2 安装依赖

```bash
pip install -r requirements.txt
```

#### 2.1.3 配置数据库

编辑 `config/default.yaml`：

```yaml
database:
  url: postgresql+asyncpg://user:password@localhost:5432/videopipeline
```

#### 2.1.4 初始化数据库

```bash
alembic upgrade head
```

#### 2.1.5 启动后端服务

```bash
# 方式 1: 一键启动所有服务
./start_all_services.sh

# 方式 2: 分别启动
# 启动 Celery Workers
./start_all_celery_workers.sh

# 启动 FastAPI 服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2.2 前端安装

#### 2.2.1 安装依赖

```bash
cd frontend
npm install
```

#### 2.2.2 配置 API 地址

编辑 `.env`：

```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

#### 2.2.3 启动前端服务

```bash
npm run dev
```

### 2.3 生产环境部署

#### 2.3.1 使用 Supervisor 管理 Celery Workers

创建 `/etc/supervisor/conf.d/videopipeline.conf`：

```ini
[program:videopipeline-celery-pipeline]
command=/path/to/backend/.venv/bin/celery -A app.celery_app worker --queue=pipeline --loglevel=info
directory=/path/to/backend
user=www-data
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
stdout_logfile=/var/log/videopipeline/celery-pipeline.log
stderr_logfile=/var/log/videopipeline/celery-pipeline-err.log

[program:videopipeline-celery-compliance]
command=/path/to/backend/.venv/bin/celery -A app.celery_app worker --queue=compliance --loglevel=info
directory=/path/to/backend
user=www-data
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
stdout_logfile=/var/log/videopipeline/celery-compliance.log
stderr_logfile=/var/log/videopipeline/celery-compliance-err.log

[program:videopipeline-celery-continuity]
command=/path/to/backend/.venv/bin/celery -A app.celery_app worker --queue=continuity --loglevel=info
directory=/path/to/backend
user=www-data
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
stdout_logfile=/var/log/videopipeline/celery-continuity.log
stderr_logfile=/var/log/videopipeline/celery-continuity-err.log
```

启动 Supervisor：

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start videopipeline-celery-*
```

#### 2.3.2 使用 Nginx 反向代理

创建 `/etc/nginx/sites-available/videopipeline`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/videopipeline /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 3. 基础操作

### 3.1 创建项目

1. 访问 http://localhost:5173
2. 点击"新建项目"
3. 填写项目信息：
   - 项目名称
   - 项目描述
   - 类型（电影、电视剧、短视频等）
   - 目标集数
   - 每集时长（分钟）
4. 点击"创建"

### 3.2 查看项目

1. 在项目列表中点击项目名称
2. 查看项目详情和流水线状态

### 3.3 删除项目

1. 在项目列表中点击项目右侧的"删除"按钮
2. 确认删除

### 3.4 编辑项目

1. 在项目详情页点击"编辑"按钮
2. 修改项目信息
3. 点击"保存"

---

## 4. 流水线管理

### 4.1 流水线概览

流水线包含 9 个阶段：

| 阶段 | 名称 | 描述 |
|------|------|------|
| S1 | 世界观与角色 | 定义世界观和角色设定 |
| S2 | 剧情大纲 | 生成整体剧情大纲 |
| S3 | 逐场景剧本 | 生成详细的场景剧本 |
| S4 | 分镜与提示词 | 生成分镜和图像生成提示词 |
| S5 | 关键帧图像 | 生成关键帧图像 |
| S6 | 视频片段 | 生成视频片段 |
| S7 | 音频合成 | 合成语音、背景音乐和音效 |
| S8 | 粗剪合成 | 粗剪合成视频 |
| S9 | 精剪出片 | 精剪出片 |

### 4.2 开始生成

1. 在项目详情页点击流水线节点
2. 点击"开始生成"按钮
3. 系统将异步生成候选内容
4. 等待生成完成

### 4.3 审核候选

1. 在阶段详情页查看生成的候选
2. 点击候选卡片查看详情
3. 选择最佳候选
4. 点击"批准"进入下一阶段

### 4.4 修改候选

1. 在候选详情页点击"编辑"
2. 修改候选内容
3. 点击"保存"

### 4.5 重做阶段

1. 在阶段详情页点击"重做"
2. 系统将重新生成候选
3. 等待生成完成

### 4.6 回退阶段

1. 在流水线概览页点击需要回退的阶段
2. 点击"回退"按钮
3. 确认回退

---

## 5. 供应商管理

### 5.1 查看供应商配置

1. 访问"供应商管理"页面
2. 查看所有能力的供应商配置

### 5.2 添加供应商

1. 点击"添加供应商"按钮
2. 填写供应商信息：
   - 供应商名称
   - 供应商类型（本地/云端）
   - 基础 URL
   - 能力类型
   - 优先级
3. 点击"保存"

### 5.3 编辑供应商

1. 在供应商列表中点击供应商名称
2. 修改供应商信息
3. 点击"保存"

### 5.4 删除供应商

1. 在供应商列表中点击供应商右侧的"删除"按钮
2. 确认删除

### 5.5 测试供应商

1. 在供应商列表中点击供应商右侧的"测试"按钮
2. 查看测试结果

### 5.6 配置能力优先级

1. 在"供应商管理"页面选择能力类型
2. 调整供应商优先级
3. 点击"保存"

---

## 6. 节点管理

### 6.1 查看节点列表

1. 访问"节点管理"页面
2. 查看所有节点的状态

### 6.2 添加节点

1. 点击"添加节点"按钮
2. 填写节点信息：
   - 节点名称
   - 节点类型
   - 基础 URL
   - 能力列表
3. 点击"保存"

### 6.3 编辑节点

1. 在节点列表中点击节点名称
2. 修改节点信息
3. 点击"保存"

### 6.4 删除节点

1. 在节点列表中点击节点右侧的"删除"按钮
2. 确认删除

### 6.5 测试节点

1. 在节点列表中点击节点右侧的"测试"按钮
2. 查看测试结果

### 6.6 查看节点状态

1. 在节点列表中查看节点状态
2. 状态包括：在线、离线、忙碌

---

## 7. 连续性管理

### 7.1 角色状态管理

#### 7.1.1 查看角色状态

1. 在项目详情页点击"角色状态"
2. 查看所有角色的状态

#### 7.1.2 创建角色状态

1. 点击"添加角色"按钮
2. 填写角色信息：
   - 角色名称
   - 角色描述
   - 初始状态
   - 开始集数
   - 结束集数
3. 点击"保存"

#### 7.1.3 编辑角色状态

1. 在角色列表中点击角色名称
2. 修改角色信息
3. 点击"保存"

#### 7.1.4 删除角色状态

1. 在角色列表中点击角色右侧的"删除"按钮
2. 确认删除

#### 7.1.5 检查角色连续性

1. 点击"检查连续性"按钮
2. 系统将异步检查角色连续性
3. 查看检查结果

### 7.2 场景资产管理

#### 7.2.1 查看场景资产

1. 在项目详情页点击"场景资产"
2. 查看所有场景的资产

#### 7.2.2 创建场景资产

1. 点击"添加场景"按钮
2. 填写场景信息：
   - 场景名称
   - 场景描述
   - 场景类型
   - 风格 LoRA 模型路径
   - 背景图像路径
   - 开始集数
   - 结束集数
3. 点击"保存"

#### 7.2.3 编辑场景资产

1. 在场景列表中点击场景名称
2. 修改场景信息
3. 点击"保存"

#### 7.2.4 删除场景资产

1. 在场景列表中点击场景右侧的"删除"按钮
2. 确认删除

#### 7.2.5 检查场景连续性

1. 点击"检查连续性"按钮
2. 系统将异步检查场景连续性
3. 查看检查结果

---

## 8. 节奏管理

### 8.1 节奏模板管理

#### 8.1.1 查看节奏模板

1. 在项目详情页点击"节奏模板"
2. 查看所有节奏模板

#### 8.1.2 创建节奏模板

1. 点击"添加模板"按钮
2. 填写模板信息：
   - 模板名称
   - 模板描述
   - 节奏规则
   - 钩子配置
3. 点击"保存"

#### 8.1.3 编辑节奏模板

1. 在模板列表中点击模板名称
2. 修改模板信息
3. 点击"保存"

#### 8.1.4 删除节奏模板

1. 在模板列表中点击模板右侧的"删除"按钮
2. 确认删除

### 8.2 节奏验证

1. 在场景详情页点击"验证节奏"按钮
2. 系统将异步验证节奏
3. 查看验证结果

---

## 9. 合规检查

### 9.1 人脸识别检查

1. 在项目详情页点击"合规检查"
2. 点击"人脸识别检查"按钮
3. 选择检查范围：
   - 全部集数
   - 指定集数
   - 指定阶段
4. 点击"开始检查"
5. 系统将异步执行检查
6. 查看检查报告

### 9.2 音乐版权检查

1. 在"合规检查"页面点击"音乐版权检查"按钮
2. 选择检查范围
3. 点击"开始检查"
4. 系统将异步执行检查
5. 查看检查报告

### 9.3 内容审核检查

1. 在"合规检查"页面点击"内容审核检查"按钮
2. 选择检查范围
3. 点击"开始检查"
4. 系统将异步执行检查
5. 查看检查报告

### 9.4 查看合规报告

1. 在"合规检查"页面查看所有报告
2. 点击报告名称查看详情
3. 查看检查结果和建议

---

## 10. 故障排除

### 10.1 常见问题

#### 问题 1: Redis 连接失败

**症状**：
```
Error: Error 111 connecting to localhost:6379. Connection refused.
```

**解决方案**：
```bash
# 检查 Redis 是否运行
redis-cli ping

# 启动 Redis
redis-server
```

#### 问题 2: PostgreSQL 连接失败

**症状**：
```
Error: connection to server at "localhost", port 5432 failed: Connection refused
```

**解决方案**：
```bash
# 检查 PostgreSQL 是否运行
pg_isready

# 启动 PostgreSQL
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql
```

#### 问题 3: Celery Worker 无法启动

**症状**：
```
Error: [Errno 48] Address already in use
```

**解决方案**：
```bash
# 检查端口占用
lsof -i :6379

# 清理 Redis 数据
redis-cli FLUSHALL

# 重启 Workers
pkill -f celery
```

#### 问题 4: 任务卡住

**症状**：
任务长时间处于"处理中"状态

**解决方案**：
```bash
# 重启 Workers
pkill -f celery

# 清除卡住的任务
celery -A app.celery_app purge

# 重新启动 Workers
./start_all_celery_workers.sh
```

#### 问题 5: 前端无法连接后端

**症状**：
前端页面显示"无法连接到服务器"

**解决方案**：
1. 检查后端是否启动
2. 检查 API 地址配置
3. 检查网络连接
4. 查看浏览器控制台错误信息

### 10.2 日志查看

#### 后端日志

```bash
# FastAPI 日志
tail -f /tmp/uvicorn.log

# Celery 日志
tail -f /tmp/celery-pipeline.log
tail -f /tmp/celery-compliance.log
tail -f /tmp/celery-continuity.log
```

#### 前端日志

打开浏览器开发者工具（F12），查看 Console 标签。

#### 数据库日志

```bash
# PostgreSQL 日志
tail -f /var/log/postgresql/postgresql-14-main.log
```

### 10.3 性能优化

#### 调整 Worker 数量

编辑 `start_all_services.sh`：

```bash
# 高性能服务器（16核+）
--concurrency=8

# 中等性能服务器（8核）
--concurrency=4

# 低性能服务器（4核）
--concurrency=2
```

#### 调整任务超时

编辑 `app/celery_app.py`：

```python
celery_app.conf.update(
    task_time_limit=3600,  # 硬超时（秒）
    task_soft_time_limit=3000,  # 软超时（秒）
)
```

#### 优化数据库查询

1. 添加适当的索引
2. 使用批量查询
3. 避免N+1查询

---

## 11. 最佳实践

### 11.1 项目管理

1. **合理规划项目**：在创建项目前，明确项目类型、集数、时长等基本信息
2. **分阶段审核**：每个阶段完成后及时审核，避免积压
3. **保留版本历史**：重要修改保留版本历史，方便回退

### 11.2 流水线管理

1. **按顺序执行**：严格按照流水线顺序执行，不要跳过阶段
2. **多候选对比**：生成多个候选，对比选择最佳方案
3. **及时审核**：生成完成后及时审核，提高效率

### 11.3 供应商管理

1. **本地优先**：优先使用本地供应商，降低成本和延迟
2. **配置备份**：定期备份供应商配置
3. **监控状态**：定期检查供应商状态，及时处理故障

### 11.4 节点管理

1. **负载均衡**：合理分配任务到不同节点
2. **健康检查**：定期检查节点健康状态
3. **故障转移**：配置故障转移，确保高可用

### 11.5 连续性管理

1. **定期检查**：定期检查角色和场景连续性
2. **及时修正**：发现问题及时修正
3. **版本控制**：重要修改保留版本历史

### 11.6 节奏管理

1. **使用模板**：使用节奏模板提高效率
2. **定期验证**：定期验证节奏是否符合要求
3. **灵活调整**：根据实际情况灵活调整节奏

### 11.7 合规检查

1. **全面检查**：定期进行全面合规检查
2. **及时修正**：发现问题及时修正
3. **保留记录**：保留检查记录，方便追溯

---

## 附录

### A. 快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl + S | 保存 |
| Ctrl + Z | 撤销 |
| Ctrl + Y | 重做 |
| Ctrl + F | 搜索 |

### B. 常用命令

```bash
# 启动所有服务
./start_all_services.sh

# 启动 Celery Workers
./start_all_celery_workers.sh

# 启动 FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端
npm run dev

# 数据库迁移
alembic upgrade head

# 查看任务状态
celery -A app.celery_app inspect active

# 清除所有任务
celery -A app.celery_app purge
```

### C. 联系方式

- 项目地址: https://github.com/your-repo/video-pipeline
- 问题反馈: https://github.com/your-repo/video-pipeline/issues
- 邮箱: support@example.com

---

**文档结束**