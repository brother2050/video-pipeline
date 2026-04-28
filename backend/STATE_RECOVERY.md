# 状态恢复系统使用指南

## 问题背景

当系统因为各种原因（如服务器重启、进程中断、网络问题等）中断时，流水线阶段可能会停留在"生成中"（generating）状态，无法自动恢复。这会导致用户无法继续操作该阶段。

## 解决方案

我们实现了一个完整的状态恢复系统，包括：

### 1. 自动检测和恢复
系统会自动检测处于"生成中"状态超过阈值的阶段，并根据情况自动恢复：
- 如果有已生成的候选：恢复到"审核"（review）状态
- 如果没有候选：恢复到"就绪"（ready）状态

### 2. 手动恢复接口
提供API接口让用户手动恢复特定阶段的状态。

### 3. 管理员接口
提供管理员接口查看和批量恢复所有卡住的阶段。

## API接口

### 1. 手动恢复单个阶段

**接口**: `POST /api/projects/{project_id}/stages/{stage_type}/recover`

**参数**:
- `project_id`: 项目ID
- `stage_type`: 阶段类型（如 worldbuilding, outline等）
- `target_status`: 目标状态（可选，默认为ready）
  - `ready`: 恢复到就绪状态
  - `review`: 恢复到审核状态

**示例**:
```bash
# 恢复到就绪状态
curl -X POST "http://localhost:8000/api/projects/{project_id}/stages/worldbuilding/recover?target_status=ready"

# 恢复到审核状态
curl -X POST "http://localhost:8000/api/projects/{project_id}/stages/worldbuilding/recover?target_status=review"
```

**响应**:
```json
{
  "success": true,
  "data": {
    "success": true,
    "message": "阶段状态已从 generating 恢复到 ready",
    "previous_status": "generating",
    "new_status": "ready"
  }
}
```

### 2. 查看卡住的阶段（管理员）

**接口**: `GET /api/admin/stages/stuck`

**响应**:
```json
{
  "success": true,
  "data": {
    "count": 2,
    "timeout_minutes": 30,
    "stages": [
      {
        "project_id": "uuid",
        "stage_type": "worldbuilding",
        "current_status": "generating",
        "last_updated": "2026-04-28T12:00:00Z",
        "stuck_duration_minutes": 45.5
      }
    ]
  }
}
```

### 3. 批量恢复所有卡住的阶段（管理员）

**接口**: `POST /api/admin/stages/recover-all`

**响应**:
```json
{
  "success": true,
  "data": {
    "message": "状态恢复完成",
    "statistics": {
      "checked": 5,
      "recovered": 2,
      "skipped": 3
    }
  }
}
```

## 配置参数

在 `app/utils/state_recovery.py` 中可以配置：

```python
# 超时时间：如果阶段在生成中状态超过这个时间，视为异常
GENERATING_TIMEOUT_MINUTES = 30
```

## 使用场景

### 场景1：世界观构建阶段卡住

**问题**: 世界观构建阶段显示"生成中"已经很久了，但没有任何进展。

**解决方案**:
```bash
# 1. 先查看阶段状态
curl "http://localhost:8000/api/projects/{project_id}/stages/worldbuilding"

# 2. 如果确认卡住，手动恢复到就绪状态
curl -X POST "http://localhost:8000/api/projects/{project_id}/stages/worldbuilding/recover?target_status=ready"

# 3. 重新生成候选
curl -X POST "http://localhost:8000/api/projects/{project_id}/stages/worldbuilding/generate" \
  -H "Content-Type: application/json" \
  -d '{"num_candidates": 3}'
```

### 场景2：批量处理多个卡住的阶段

**问题**: 系统重启后，多个阶段都卡在"生成中"状态。

**解决方案**:
```bash
# 1. 查看所有卡住的阶段
curl "http://localhost:8000/api/admin/stages/stuck"

# 2. 批量恢复所有卡住的阶段
curl -X POST "http://localhost:8000/api/admin/stages/recover-all"
```

### 场景3：部分生成成功但未完成

**问题**: 生成过程中断，但已经有部分候选生成成功。

**解决方案**:
```bash
# 恢复到审核状态，可以查看已生成的候选
curl -X POST "http://localhost:8000/api/projects/{project_id}/stages/worldbuilding/recover?target_status=review"

# 查看已生成的候选
curl "http://localhost:8000/api/projects/{project_id}/stages/worldbuilding/candidates"
```

## 日志记录

所有状态恢复操作都会记录到日志中：

```
2026-04-28 12:38:32 - app.utils.state_recovery - WARNING - [state_recovery.py:45] - 阶段 worldbuilding (项目: xyz) 已卡在生成中状态超过 30 分钟，最后更新时间: 2026-04-28T12:00:00Z
2026-04-28 12:38:32 - app.utils.state_recovery - INFO - [state_recovery.py:55] - 恢复阶段 worldbuilding 到审核状态 (有 2 个候选)
2026-04-28 12:38:32 - app.routers.stages - WARNING - [stages.py:397] - 手动恢复阶段状态 - 项目: xyz, 阶段: worldbuilding, 当前状态: generating, 目标状态: ready
```

## 注意事项

1. **超时阈值**: 默认为30分钟，可根据实际情况调整
2. **数据安全**: 恢复操作不会删除已生成的候选数据
3. **权限控制**: 管理员接口需要适当的权限控制
4. **日志监控**: 建议定期检查日志，及时发现卡住的阶段
5. **定期维护**: 可以设置定时任务定期执行批量恢复

## 前端集成建议

### 1. 添加恢复按钮
在阶段页面添加"恢复状态"按钮，当检测到阶段卡住时显示。

```typescript
const handleRecoverStage = async (stageType: string, targetStatus: 'ready' | 'review') => {
  try {
    const response = await fetch(`/api/projects/${projectId}/stages/${stageType}/recover?target_status=${targetStatus}`, {
      method: 'POST',
    });
    const result = await response.json();
    if (result.success) {
      toast.success('阶段状态已恢复');
      // 刷新阶段数据
      refetch();
    }
  } catch (error) {
    toast.error('恢复失败');
  }
};
```

### 2. 自动检测卡住的阶段
定期检查阶段状态，如果发现长时间处于"生成中"状态，提示用户。

```typescript
useEffect(() => {
  const interval = setInterval(() => {
    stages.forEach(stage => {
      if (stage.status === 'generating') {
        const lastUpdate = new Date(stage.updated_at);
        const stuckDuration = Date.now() - lastUpdate.getTime();
        if (stuckDuration > 30 * 60 * 1000) { // 30分钟
          // 显示恢复提示
          showRecoveryPrompt(stage);
        }
      }
    });
  }, 60000); // 每分钟检查一次

  return () => clearInterval(interval);
}, [stages]);
```

### 3. 管理员面板
添加管理员面板查看和批量恢复卡住的阶段。

```typescript
const AdminStuckStagesPanel = () => {
  const { data: stuckStages } = useQuery(['stuck-stages'], 
    () => fetch('/api/admin/stages/stuck').then(r => r.json())
  );

  const handleRecoverAll = async () => {
    await fetch('/api/admin/stages/recover-all', { method: 'POST' });
    toast.success('已批量恢复所有卡住的阶段');
    refetch();
  };

  return (
    <div>
      <h2>卡住的阶段 ({stuckStages?.count || 0})</h2>
      <Button onClick={handleRecoverAll}>批量恢复</Button>
      {/* 显示卡住的阶段列表 */}
    </div>
  );
};
```

## 故障排查

### 问题1: 恢复后状态没有更新
**原因**: 可能是前端缓存问题
**解决**: 刷新页面或清除缓存

### 问题2: 恢复后仍然无法生成
**原因**: 可能是Celery任务队列问题
**解决**: 检查Celery服务状态，重启Celery worker

### 问题3: 批量恢复失败
**原因**: 数据库连接问题
**解决**: 检查数据库连接，逐个恢复

## 总结

状态恢复系统提供了完整的解决方案来处理中断导致的异常状态：

1. **自动检测**: 定期检查卡住的阶段
2. **智能恢复**: 根据是否有候选自动选择目标状态
3. **手动干预**: 提供API接口让用户手动恢复
4. **管理员工具**: 批量处理和监控工具
5. **完整日志**: 记录所有恢复操作便于追踪

这个系统可以有效解决"世界观构建生成中"状态不变的问题，确保系统的稳定性和可用性。