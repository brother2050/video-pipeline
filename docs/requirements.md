# VideoPipeline 需求文档

## 1. 项目背景与目标

VideoPipeline 是一套全本地化、分布式、人在回路的视频生产系统。从题材输入到电视剧品质成片，全流程在自有设备上运行。支持接入免费/付费云端 API 作为补充，本地和云端可自由混合组合。

## 2. 核心需求

### 2.1 全本地化，零外部付费
- 所有推理在自有设备完成
- 支持接入免费云端 API（GLM、Gemini、硅基流动免费模型等）

- 支持主流云端供应商（OpenAI、Kimi、DeepSeek、通义千问等）
- 本地和云端可自由混合组合

### 2.2 分布式架构
- 每台机器专职跑一类服务，对外暴露标准 API
- 编排层统一调度各节点
- 供应商系统包裹本地节点，统一抽象层

### 2.3 人在回路，质量可控
- 每个阶段必须有人工审核门控
- 人可以修改、重做、回退任何阶段
- 每个素材生成多张候选，人从中选最好的
- 提示词可直接编辑
- 版本历史完整保留

### 2.4 跨平台
- 支持 Linux / macOS / Windows
- 不使用 Docker
- Python 虚拟环境 + 系统包管理

### 2.5 个人使用，轻量部署
- 配置文件 + Web 页面管理
- 一台机器也能跑，多台更好

### 2.6 页面化管理
- 所有节点管理通过 Web 页面完成
- 配置变更即时生效

### 2.7 本地永不中断
- 远程供应商故障时本地供应商自动接管
- 流水线不停工

## 3. 九阶段流水线

| 阶段 | 名称 | 使用能力 | 输出 |
|---|---|---|---|
| S1 | 世界观与角色 | LLM | JSON |
| S2 | 剧情大纲 | LLM | JSON |
| S3 | 逐场景剧本 | LLM | JSON |
| S4 | 分镜与提示词 | LLM | JSON |
| S5 | 关键帧图像 | IMAGE | PNG |
| S6 | 视频片段 | VIDEO | MP4 |
| S7 | 音频合成 | TTS+BGM+SFX | WAV |
| S8 | 粗剪合成 | POST(FFmpeg) | MP4 |
| S9 | 精剪出片 | POST(FFmpeg) | MP4 |

## 4. 供应商体系

支持 7 种能力：LLM、IMAGE、VIDEO、TTS、BGM、SFX、POST。
每种能力可配多个供应商，按优先级调度，失败自动降级。

ComfyUI 适配器采用工作流 JSON 模板驱动方式，自动分析工作流结构，通过参数覆盖注入提示词、尺寸、模型等参数。支持前端导入自定义工作流 JSON。

SD WebUI 适配器使用原生 API（/sdapi/v1/txt2img、/sdapi/v1/img2img）。

## 5. 技术架构

三层架构：Web 管理界面 → 编排中枢 → 供应商抽象层 → 本地/云端节点。

## 6. 数据模型

7 张表：projects、stages、candidates、artifacts、versions、nodes、capability_configs。

## 7. API 端点

详见 shared-contract.md 中的完整端点列表。

## 8. 非功能需求

- Python 3.11+，TypeScript strict 模式
- 零占位代码，零类型告警
- 接口前后端完全一致
- 不使用 Docker
