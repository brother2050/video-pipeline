# 前端状态恢复功能使用指南

## 功能概述

在前端界面上添加了状态恢复功能，让您可以直接在界面上操作，无需手动调用API接口。当阶段因为中断导致状态一直停留在"生成中"时，系统会自动检测并提供恢复按钮。

## 界面位置

### 1. 流水线总览页 (PipelineView)

**位置**: 项目流水线页面，每个阶段节点下方

**显示条件**: 当阶段处于"生成中"状态超过30分钟时

**功能特点**:
- 自动检测卡住的阶段
- 在阶段节点下方显示红色"恢复"按钮
- 点击按钮即可恢复阶段状态
- 智能选择目标状态（有候选→审核，无候选→就绪）

**界面示例**:
```
┌─────────────┐
│   [图标]    │ ← 阶段节点
└─────────────┘
  世界观构建
  1/9
  2 候选
  🔄 恢复     ← 恢复按钮（红色）
  [状态标签]
```

### 2. 阶段详情页 (StageReview)

**位置**: 左侧面板，生成按钮下方

**显示条件**: 当阶段处于"生成中"状态超过30分钟时

**功能特点**:
- 显示醒目的红色警告框
- 说明阶段已卡住的原因
- 提供详细的恢复按钮
- 恢复时显示加载动画

**界面示例**:
```
┌─────────────────────────────┐
│ 生成数量: [3]              │
│ [生成] 按钮                │
│                            │
│ ┌─────────────────────────┐ │
│ │ ⚠️ 阶段已卡住          │ │
│ │ 该阶段处于"生成中"状态   │ │
│ │ 超过30分钟，可能已中断  │ │
│ │                         │ │
│ │ [🔄 恢复状态] 按钮      │ │
│ └─────────────────────────┘ │
└─────────────────────────────┘
```

## 使用流程

### 场景1: 在流水线总览页恢复

1. **打开项目流水线页面**
   - 访问 `/projects/{project_id}`
   - 查看9个阶段的状态

2. **识别卡住的阶段**
   - 查找显示"🔄 恢复"按钮的阶段
   - 该按钮为红色，表示阶段已卡住

3. **点击恢复按钮**
   - 点击"恢复"按钮
   - 系统自动选择目标状态
   - 等待恢复完成

4. **确认恢复结果**
   - 查看状态变化
   - 阶段状态会从"生成中"变为"就绪"或"审核"
   - 恢复按钮会自动消失

### 场景2: 在阶段详情页恢复

1. **打开阶段详情页**
   - 在流水线页面点击卡住的阶段
   - 进入 `/projects/{project_id}/stages/{stage_type}`

2. **查看警告信息**
   - 左侧面板会显示红色警告框
   - 说明阶段已卡住超过30分钟

3. **点击恢复状态按钮**
   - 点击"恢复状态"按钮
   - 按钮会显示旋转动画
   - 等待恢复完成

4. **确认恢复结果**
   - 警告框会自动消失
   - 阶段状态恢复正常
   - 可以重新生成或审核候选

## 智能恢复逻辑

系统会根据以下规则自动选择目标状态：

### 规则1: 有候选存在
- **条件**: 阶段已有生成的候选内容
- **目标状态**: 审核状态 (review)
- **原因**: 部分生成成功，可以直接审核

### 规则2: 无候选存在
- **条件**: 阶段没有任何候选内容
- **目标状态**: 就绪状态 (ready)
- **原因**: 生成完全失败，需要重新生成

## 检测机制

### 自动检测
- **检测频率**: 实时检测
- **检测条件**: 阶段状态为"生成中"
- **超时阈值**: 30分钟
- **检测依据**: 阶段的 `updated_at` 时间戳

### 检测逻辑
```typescript
const STUCK_THRESHOLD_MINUTES = 30;
const now = Date.now();
const updatedTime = new Date(stage.updated_at).getTime();
const stuckDuration = (now - updatedTime) / (1000 * 60);

if (stuckDuration > STUCK_THRESHOLD_MINUTES) {
  // 标记为卡住，显示恢复按钮
}
```

## 用户体验优化

### 1. 视觉提示
- **红色警告**: 使用醒目的红色表示异常状态
- **图标提示**: 使用 `AlertTriangle` 和 `RefreshCw` 图标
- **加载动画**: 恢复时显示旋转动画

### 2. 操作反馈
- **成功提示**: 显示"恢复成功"的toast消息
- **失败提示**: 显示"恢复失败"的toast消息
- **状态更新**: 自动刷新阶段数据

### 3. 防误操作
- **禁用状态**: 恢复进行时禁用按钮
- **加载状态**: 显示加载动画
- **自动隐藏**: 恢复成功后自动隐藏恢复按钮

## 技术实现

### 前端组件

#### PipelineView.tsx
```typescript
// 状态管理
const [stuckStages, setStuckStages] = useState<Set<string>>(new Set());

// 恢复mutation
const recoverMutation = useRecoverStage(id || "", "");

// 检测卡住的阶段
useEffect(() => {
  if (!stages) return;

  const STUCK_THRESHOLD_MINUTES = 30;
  const now = Date.now();
  const newStuckStages = new Set<string>();

  stages.forEach(stage => {
    if (stage.status === StageStatus.GENERATING && stage.updated_at) {
      const updatedTime = new Date(stage.updated_at).getTime();
      const stuckDuration = (now - updatedTime) / (1000 * 60);
      
      if (stuckDuration > STUCK_THRESHOLD_MINUTES) {
        newStuckStages.add(stage.stage_type);
      }
    }
  });

  setStuckStages(newStuckStages);
}, [stages]);
```

#### StageReview.tsx
```typescript
// 卡住状态检测
const [isStuck, setIsStuck] = useState(false);

useEffect(() => {
  if (!stage) return;

  const STUCK_THRESHOLD_MINUTES = 30;
  const now = Date.now();

  if (stage.status === StageStatus.GENERATING && stage.updated_at) {
    const updatedTime = new Date(stage.updated_at).getTime();
    const stuckDuration = (now - updatedTime) / (1000 * 60);
    
    setIsStuck(stuckDuration > STUCK_THRESHOLD_MINUTES);
  } else {
    setIsStuck(false);
  }
}, [stage]);
```

### API集成

#### useStages.ts
```typescript
export function useRecoverStage(projectId: string, stageType: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data?: { target_status?: "ready" | "review" }) =>
      stageApi.recoverStage(projectId, stageType, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["stages", projectId] });
      qc.invalidateQueries({ queryKey: ["stage", projectId, stageType] });
      qc.invalidateQueries({ queryKey: ["project", projectId] });
    },
  });
}
```

#### stages.ts (API)
```typescript
recoverStage: async (projectId: string, stageType: string, data?: StageRecoveryRequest): Promise<StageRecoveryResponse> => {
  const params = data?.target_status ? `?target_status=${data.target_status}` : "";
  const resp = await client.post(`/projects/${projectId}/stages/${stageType}/recover${params}`);
  return resp.data as StageRecoveryResponse;
},
```

## 常见问题

### Q1: 为什么我的阶段没有显示恢复按钮？
**A**: 恢复按钮只在以下情况下显示：
- 阶段状态为"生成中"
- 超过30分钟没有更新
- 请检查阶段状态和更新时间

### Q2: 恢复后原来的候选数据会丢失吗？
**A**: 不会。恢复操作只会更新阶段状态，不会删除任何已生成的候选数据。

### Q3: 可以手动指定恢复到什么状态吗？
**A**: 系统会自动选择最合适的状态：
- 有候选：恢复到"审核"状态
- 无候选：恢复到"就绪"状态

### Q4: 恢复失败怎么办？
**A**: 
1. 检查网络连接
2. 刷新页面重试
3. 查看后端日志
4. 联系技术支持

### Q5: 30分钟的超时时间可以调整吗？
**A**: 可以。修改以下代码中的常量：
```typescript
const STUCK_THRESHOLD_MINUTES = 30; // 改为您需要的时间
```

## 最佳实践

### 1. 定期检查
- 定期查看流水线页面
- 注意显示恢复按钮的阶段
- 及时处理卡住的阶段

### 2. 预防措施
- 确保服务器稳定运行
- 避免频繁重启服务
- 监控Celery任务队列

### 3. 数据备份
- 定期备份项目数据
- 记录重要阶段的候选
- 建立恢复流程

## 总结

前端状态恢复功能提供了直观、易用的界面操作方式：

✅ **自动检测**: 实时检测卡住的阶段
✅ **智能恢复**: 自动选择目标状态
✅ **直观界面**: 醒目的视觉提示
✅ **操作简单**: 一键恢复状态
✅ **实时反馈**: 即时显示操作结果

无需手动调用API接口，直接在界面上操作，大大提升了用户体验和操作效率！