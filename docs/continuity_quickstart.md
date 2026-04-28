# 多集短剧连续性管理系统 - 快速启动指南

## 🚀 5 分钟快速开始

### 步骤 1：数据库迁移

```bash
cd backend
alembic upgrade head
```

### 步骤 2：初始化节奏模板

```bash
python scripts/init_pacing_templates.py
```

### 步骤 3：启动服务

```bash
python scripts/start.py
```

### 步骤 4：验证安装

访问 http://localhost:8000/docs 查看 API 文档

---

## 📖 核心概念

### 1. 角色状态机（Character State）

管理角色在不同集数的状态变化，确保角色一致性。

**示例：**
```json
{
  "character_name": "主角",
  "episode_start": 1,
  "episode_end": 5,
  "outfit_description": "崭新制服",
  "hairstyle": "短发",
  "accessories": {
    "项链": "银色十字架项链"
  },
  "signature_items": {
    "项链": "银色十字架项链，主角的标志性物品"
  }
}
```

### 2. 场景资产库（Scene Asset）

管理可复用的场景资产，确保场景一致性。

**示例：**
```json
{
  "scene_name": "主角卧室",
  "scene_type": "interior",
  "description": "现代简约风格的卧室",
  "layout_description": "床靠墙，窗户在右侧，书桌在左侧",
  "variants": {
    "day": {
      "lighting": "自然光",
      "weather": "晴天"
    },
    "night": {
      "lighting": "暖色灯光",
      "weather": "夜晚"
    }
  }
}
```

### 3. 节奏模板（Pacing Template）

定义短剧的叙事节奏结构，确保节奏统一。

**示例：**
```json
{
  "name": "反转-打脸-悬念",
  "genre": "drama",
  "structure": {
    "sections": [
      {
        "type": "setup",
        "name": "铺垫",
        "duration_sec": 15,
        "description": "建立情境，引入冲突"
      },
      {
        "type": "twist",
        "name": "反转",
        "duration_sec": 20,
        "description": "剧情反转，打破预期"
      },
      {
        "type": "climax",
        "name": "高潮",
        "duration_sec": 15,
        "description": "打脸时刻，情感爆发"
      },
      {
        "type": "cliffhanger",
        "name": "悬念",
        "duration_sec": 10,
        "description": "留下悬念，引导下一集"
      }
    ]
  }
}
```

### 4. 合规检查（Compliance Check）

检查内容的合规性，避免违规风险。

**检查类型：**
- **人脸合规** - 检查是否使用禁止的人脸
- **音乐版权** - 检查音乐是否涉及版权问题
- **内容合规** - 检查敏感词、暴力、色情等

---

## 💡 使用场景

### 场景 1：创建多集短剧项目

1. 创建项目
2. 为每个主要角色创建角色状态机
3. 为核心场景创建场景资产
4. 选择合适的节奏模板
5. 开始生成内容

### 场景 2：检查角色一致性

在生成第 10 集之前，检查第 1-9 集的角色状态是否一致：

```bash
curl -X POST http://localhost:8000/api/continuity/checks/character?project_id=xxx&episode_start=1&episode_end=9
```

### 场景 3：验证单集节奏

生成剧本后，验证是否符合节奏模板：

```bash
curl -X POST http://localhost:8000/api/pacing/validate/pacing?template_id=xxx \
  -H "Content-Type: application/json" \
  -d '{
    "scenes": [...]
  }'
```

### 场景 4：执行合规检查

在发布前，执行所有合规检查：

```bash
curl -X POST http://localhost:8000/api/compliance/check/all?project_id=xxx \
  -H "Content-Type: application/json" \
  -d '{
    "characters": [...],
    "bgm_plan": [...]
  }'
```

---

## 🔧 API 端点速查

### 连续性管理（Continuity）

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/continuity/characters/states` | 创建角色状态 |
| GET | `/api/continuity/characters/states/{project_id}/{character_name}/{episode_number}` | 获取角色状态 |
| POST | `/api/continuity/scenes/assets` | 创建场景资产 |
| GET | `/api/continuity/scenes/assets/{project_id}/{scene_name}` | 获取场景资产 |
| POST | `/api/continuity/checks/character` | 检查角色一致性 |
| POST | `/api/continuity/checks/scene` | 检查场景一致性 |
| GET | `/api/continuity/prompts/character` | 构建角色提示词 |
| GET | `/api/continuity/prompts/scene` | 构建场景提示词 |

### 节奏控制（Pacing）

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/pacing/templates` | 创建节奏模板 |
| GET | `/api/pacing/templates/{template_id}` | 获取节奏模板 |
| GET | `/api/pacing/templates/genre/{genre}` | 按类型获取模板 |
| POST | `/api/pacing/validate/hook-3sec` | 验证黄金3秒 |
| POST | `/api/pacing/validate/cliffhanger` | 验证结尾钩子 |
| POST | `/api/pacing/validate/pacing` | 验证整体节奏 |
| GET | `/api/pacing/prompts/{template_id}/{episode_number}` | 构建节奏提示词 |

### 合规检查（Compliance）

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/compliance/check/face` | 检查人脸合规性 |
| POST | `/api/compliance/check/music` | 检查音乐版权 |
| POST | `/api/compliance/check/content` | 检查内容合规性 |
| POST | `/api/compliance/check/all` | 执行所有检查 |
| GET | `/api/compliance/prompts/compliance` | 获取合规提示词 |

---

## 🎯 最佳实践

### 1. 角色状态管理

- ✅ 为每个主要角色创建状态机
- ✅ 设置合理的集数范围
- ✅ 定义标志性物品并强制出现
- ✅ 定期执行一致性检查

### 2. 场景资产管理

- ✅ 为核心场景创建资产
- ✅ 使用 ControlNet 锁定场景结构
- ✅ 预设时间/天气变体
- ✅ 保存参考图用于一致性检查

### 3. 节奏控制

- ✅ 选择合适的节奏模板
- ✅ 严格遵守黄金3秒法则
- ✅ 每集结尾必须有悬念
- ✅ 定期验证节奏结构

### 4. 合规检查

- ✅ 在每个阶段生成后执行检查
- ✅ 在发布前执行全面检查
- ✅ 及时修复发现的违规问题
- ✅ 保留检查记录作为证据

---

## 🐛 常见问题

### Q1: 如何修改已创建的角色状态？

A: 目前系统不支持直接修改，建议创建新的状态记录并设置正确的集数范围。

### Q2: 节奏模板可以自定义吗？

A: 可以！使用 `POST /api/pacing/templates` 创建自定义模板。

### Q3: 合规检查会阻止内容生成吗？

A: 不会。合规检查是独立的验证步骤，不会阻止生成，但建议在发布前执行检查。

### Q4: 如何添加新的敏感词？

A: 修改 [compliance_service.py](file:///Users/andrew/workspace/video-pipeline/backend/app/services/compliance_service.py) 中的 `SENSITIVE_KEYWORDS` 字典。

### Q5: 系统支持多少集的短剧？

A: 理论上没有限制，但建议单季不超过 100 集，以保证管理效率。

---

## 📚 相关文档

- [完整实现文档](continuity_implementation.md)
- [API 文档](http://localhost:8000/docs)
- [多集短剧制作指南](../README.md)

---

## 🆘 获取帮助

如有问题，请：
1. 查看 API 文档
2. 阅读完整实现文档
3. 检查代码注释
4. 提交 Issue

---

**祝您创作出精彩的多集短剧！** 🎬✨