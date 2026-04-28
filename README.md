# VideoPipeline

全本地化、分布式、人在回路的视频生产系统。

## 📋 项目简介

VideoPipeline 是一套全本地化、分布式、人在回路的视频生产系统。从题材输入到电视剧品质成片，全流程在自有设备上运行。支持接入免费/付费云端 API 作为补充，本地和云端可自由混合组合。

### ✨ 核心特性

- **全本地化**：所有推理在自有设备完成，零外部付费依赖
- **分布式架构**：支持多节点协同工作，提高生产效率
- **人在回路**：每个阶段必须有人工审核门控，确保质量可控
- **跨平台支持**：支持 Linux / macOS / Windows
- **轻量部署**：配置文件 + Web 页面管理，一台机器也能跑
- **高可用性**：远程供应商故障时本地供应商自动接管，流水线不停工

## 🏗️ 系统架构

```
┌─────────────────────────────────┐
│         Web 管理界面             │
│    React + TypeScript + Vite    │
└──────────────┬──────────────────┘
               │ REST + WebSocket
┌──────────────▼──────────────────┐
│         编排中枢 (FastAPI)        │
│  流水线引擎 / 审核门控 / 路由      │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│       供应商抽象层               │
│  优先级调度 / 弹性降级 / 健康追踪  │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  本地节点          云端服务       │
│  Ollama            OpenAI       │
│  ComfyUI           DeepSeek     │
│  SD WebUI          硅基流动      │
│  CosyVoice         Gemini       │
│  MusicGen          通义千问      │
│  FFmpeg            ...          │
└─────────────────────────────────┘
```

## 🚀 快速开始

### 系统要求

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

### 安装步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd video-pipeline

# 2. 后端安装
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. 配置数据库
# 启动 PostgreSQL
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux
createdb videopipeline

# 4. 配置环境变量
# 在 backend/.env 中添加：
VP_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/videopipeline
VP_CELERY_BROKER_URL=redis://localhost:6379/0
VP_CELERY_RESULT_BACKEND=redis://localhost:6379/1

# 5. 初始化数据库
alembic upgrade head

# 6. 前端安装
cd ../frontend
npm install

# 7. 配置前端环境
# 在 frontend/.env 中添加：
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

### 启动服务

```bash
# 启动后端服务
cd backend
source .venv/bin/activate

# 启动 Celery Workers
./start_all_celery_workers.sh

# 启动 FastAPI 服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端服务
cd ../frontend
npm run dev
```

### 访问系统

- **前端界面**: http://localhost:5173
- **API 文档**: http://localhost:8000/docs
- **Flower 监控**: http://localhost:5555

## 📁 项目结构

```
video-pipeline/
├── backend/              # 后端服务
│   ├── app/             # 应用代码
│   │   ├── api/         # API 路由
│   │   ├── models/      # 数据模型
│   │   ├── schemas/     # Pydantic 模型
│   │   ├── services/    # 业务逻辑
│   │   ├── suppliers/   # 供应商适配器
│   │   ├── tasks/       # Celery 任务
│   │   └── main.py     # FastAPI 应用
│   ├── alembic/         # 数据库迁移
│   ├── config/          # 配置文件
│   └── requirements.txt # Python 依赖
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── components/  # React 组件
│   │   ├── pages/       # 页面组件
│   │   ├── hooks/       # 自定义 Hooks
│   │   ├── api/         # API 客户端
│   │   └── types/       # TypeScript 类型
│   └── package.json     # Node.js 依赖
├── docs/               # 文档
│   ├── 需求文档.md     # 项目需求文档
│   └── 操作手册.md     # 用户操作手册
├── config/             # 配置文件
├── scripts/            # 安装/启动脚本
└── data/              # 运行时数据
```

## 📚 文档

- [需求文档](docs/需求文档.md) - 完整的项目需求文档
- [操作手册](docs/操作手册.md) - 详细的用户操作指南

## 🛠️ 技术栈

**后端**：Python 3.11+ / FastAPI / SQLAlchemy 2.0 / PostgreSQL / Celery / Redis

**前端**：TypeScript / React 18 / Vite / shadcn/ui / Tailwind CSS / TanStack Query

## 🎯 核心功能

1. **项目管理** - 创建、编辑、删除项目
2. **流水线管理** - 九阶段流水线执行、异步任务处理
3. **供应商管理** - 本地和云端供应商配置、优先级调度
4. **节点管理** - 节点添加和删除、状态监控
5. **连续性管理** - 角色状态管理、场景资产管理
6. **节奏管理** - 节奏模板管理、节奏验证
7. **合规检查** - 人脸识别、音乐版权、内容审核

## 🐛 常见问题

### Redis 连接失败

```bash
# 检查 Redis 是否运行
redis-cli ping

# 启动 Redis
redis-server
```

### PostgreSQL 连接失败

```bash
# 检查 PostgreSQL 是否运行
pg_isready

# 启动 PostgreSQL
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux
```

### Celery Worker 无法启动

```bash
# 重启 Workers
pkill -f celery

# 清除卡住的任务
celery -A app.celery_app purge

# 重新启动 Workers
./start_all_celery_workers.sh
```

更多故障排除信息，请参考 [操作手册](docs/操作手册.md)。

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📞 联系方式

- 项目地址: https://github.com/your-repo/video-pipeline
- 问题反馈: https://github.com/your-repo/video-pipeline/issues
- 邮箱: support@example.com

---

**VideoPipeline** - 让视频生产更简单、更高效、更可控！