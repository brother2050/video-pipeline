# VideoPipeline

全本地化、分布式、人在回路的视频生产系统。

## 架构

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

## 快速开始

```bash
# 检查环境
python scripts/check_env.py

# 安装
python scripts/install.py

# 启动
python scripts/start.py
```

访问 http://localhost:5173

## 技术栈

- **后端**: Python 3.11+ / FastAPI / SQLAlchemy 2.0 / Pydantic v2
- **前端**: TypeScript / React 18 / Vite 6 / TailwindCSS / shadcn/ui
- **通信**: REST API + WebSocket
- **存储**: SQLite(开发) / PostgreSQL(生产) + 本地文件系统

## 目录结构

```
video-pipeline/
├── backend/          # 后端服务
├── frontend/         # 前端应用
├── config/           # 配置文件
├── scripts/          # 安装/启动脚本
├── docs/             # 文档
└── data/             # 运行时数据
```

## 文档

- [需求文档](docs/requirements.md)
- [使用指南](docs/user-guide.md)
