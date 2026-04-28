# 连续性管理功能测试指南

## 🚀 启动服务

### 1. 启动后端服务

```bash
cd /Users/andrew/workspace/video-pipeline/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 启动前端服务

```bash
cd /Users/andrew/workspace/video-pipeline/frontend
npm run dev
```

### 3. 访问应用

- **前端**: http://localhost:5173
- **后端 API 文档**: http://localhost:8000/docs

## 📋 功能测试清单

### 1. 角色状态管理 (`/projects/:id/characters`)

#### 测试步骤：
1. 访问项目详情页
2. 点击"角色状态"标签
3. 点击"添加角色状态"按钮
4. 填写表单：
   - 角色名称：主角
   - 起始剧集：1
   - 结束剧集：留空
   - 服装描述：白色衬衫，黑色裤子
   - 发型：短发
   - 妆容：淡妆
   - 年龄外观：20岁
5. 点击"创建"按钮
6. 验证角色状态是否显示在列表中
7. 点击编辑按钮，修改角色信息
8. 点击删除按钮，确认删除

#### 预期结果：
- ✅ 角色状态创建成功
- ✅ 角色状态显示在列表中
- ✅ 编辑功能正常
- ✅ 删除功能正常
- ✅ 表单验证正常

### 2. 场景资产管理 (`/projects/:id/scenes`)

#### 测试步骤：
1. 访问项目详情页
2. 点击"场景资产"标签
3. 点击"添加场景资产"按钮
4. 填写表单：
   - 场景名称：客厅
   - 场景类型：室内
   - 场景描述：现代简约风格客厅，有沙发和茶几
   - 布局描述：沙发在左侧，茶几在中间，电视在右侧
5. 点击"创建"按钮
6. 验证场景资产是否显示在列表中
7. 点击编辑按钮，修改场景信息
8. 点击删除按钮，确认删除

#### 预期结果：
- ✅ 场景资产创建成功
- ✅ 场景资产显示在列表中
- ✅ 编辑功能正常
- ✅ 删除功能正常
- ✅ 场景类型图标正确显示

### 3. 节奏模板管理 (`/projects/:id/pacing`)

#### 测试步骤：
1. 访问项目详情页
2. 点击"节奏模板"标签
3. 查看预设的3个节奏模板
4. 点击"添加模板"按钮
5. 填写表单：
   - 模板名称：测试模板
   - 类型：test
   - 目标时长：60
   - 结构配置：`{"sections": [{"type": "setup", "duration_sec": 30}]}`
6. 点击"创建"按钮
7. 点击"验证节奏"按钮
8. 选择模板，输入场景内容：
   ```json
   {
     "action": "主角走进房间，看到桌子上的信",
     "dialogue": ["这是什么？"]
   }
   ```
9. 点击"验证"按钮
10. 查看验证结果

#### 预期结果：
- ✅ 预设模板显示正常
- ✅ 模板创建成功
- ✅ 编辑功能正常
- ✅ 删除功能正常
- ✅ 节奏验证功能正常
- ✅ 验证结果正确显示

### 4. 合规检查 (`/projects/:id/compliance`)

#### 测试步骤：
1. 访问项目详情页
2. 点击"合规检查"标签
3. 点击"启动检查"按钮
4. 填写表单：
   - 检查类型：人脸识别
   - 剧集编号：留空
   - 阶段类型：留空
5. 点击"启动检查"按钮
6. 等待检查完成
7. 点击报告详情按钮
8. 查看检查结果

#### 预期结果：
- ✅ 检查启动成功
- ✅ 检查报告显示在列表中
- ✅ 报告详情显示正常
- ✅ 违规信息正确显示
- ✅ 状态图标正确显示

## 🔍 API 测试

### 使用 Swagger UI 测试

1. 访问 http://localhost:8000/docs
2. 测试以下 API：

#### 角色状态 API
- `POST /api/continuity/characters/states` - 创建角色状态
- `GET /api/continuity/characters/states` - 获取角色状态列表
- `GET /api/continuity/characters/states/{state_id}` - 获取单个角色状态
- `PUT /api/continuity/characters/states/{state_id}` - 更新角色状态
- `DELETE /api/continuity/characters/states/{state_id}` - 删除角色状态

#### 场景资产 API
- `POST /api/continuity/scenes/assets` - 创建场景资产
- `GET /api/continuity/scenes/assets` - 获取场景资产列表
- `GET /api/continuity/scenes/assets/{asset_id}` - 获取单个场景资产
- `PUT /api/continuity/scenes/assets/{asset_id}` - 更新场景资产
- `DELETE /api/continuity/scenes/assets/{asset_id}` - 删除场景资产

#### 节奏模板 API
- `GET /api/pacing/templates` - 获取节奏模板列表
- `GET /api/pacing/templates/{template_id}` - 获取单个节奏模板
- `POST /api/pacing/templates` - 创建节奏模板
- `PUT /api/pacing/templates/{template_id}` - 更新节奏模板
- `DELETE /api/pacing/templates/{template_id}` - 删除节奏模板
- `POST /api/pacing/validate` - 验证节奏

#### 合规检查 API
- `POST /api/compliance/check` - 执行合规检查
- `GET /api/compliance/reports` - 获取合规报告列表
- `GET /api/compliance/reports/{report_id}` - 获取单个合规报告

## 🐛 常见问题

### 1. 页面无法加载

**问题**：访问页面时显示"加载中..."或错误

**解决方案**：
- 检查后端服务是否启动
- 检查 API 地址是否正确
- 查看浏览器控制台错误信息
- 检查网络连接

### 2. 数据无法保存

**问题**：点击保存按钮后没有反应或显示错误

**解决方案**：
- 检查表单必填字段是否填写
- 检查数据格式是否正确
- 查看后端日志
- 检查数据库连接

### 3. API 请求失败

**问题**：API 请求返回 404 或 500 错误

**解决方案**：
- 检查 API 路径是否正确
- 检查后端路由是否正确配置
- 查看后端日志
- 检查数据库表是否存在

### 4. 页面样式异常

**问题**：页面显示不正常或样式错乱

**解决方案**：
- 清除浏览器缓存
- 检查 Tailwind CSS 是否正确加载
- 检查组件导入是否正确
- 重新启动前端服务

## 📊 性能测试

### 1. 加载时间测试

- 测试页面首次加载时间
- 测试数据加载时间
- 测试页面切换时间

### 2. 并发测试

- 同时创建多个角色状态
- 同时创建多个场景资产
- 测试并发请求处理能力

### 3. 数据量测试

- 创建大量角色状态（100+）
- 创建大量场景资产（100+）
- 测试页面渲染性能

## ✅ 验收标准

### 功能完整性
- [ ] 所有 CRUD 操作正常工作
- [ ] 表单验证正确
- [ ] 错误处理完善
- [ ] 加载状态正确显示

### 用户体验
- [ ] 界面美观易用
- [ ] 操作流畅无卡顿
- [ ] 错误提示清晰
- [ ] 响应式设计正常

### 代码质量
- [ ] 代码结构清晰
- [ ] 注释完整
- [ ] 无明显 bug
- [ ] 性能良好

## 🎯 下一步优化

1. **功能增强**
   - 添加图片上传功能
   - 添加批量操作功能
   - 添加导出功能
   - 添加历史记录功能

2. **性能优化**
   - 实现虚拟滚动
   - 优化数据加载
   - 添加缓存机制
   - 优化渲染性能

3. **用户体验**
   - 添加快捷键支持
   - 优化移动端体验
   - 添加拖拽功能
   - 添加动画效果

## 📞 反馈与支持

如果遇到问题或有建议，请：
1. 查看本文档
2. 检查后端日志
3. 查看浏览器控制台
4. 提交 Issue 或 PR