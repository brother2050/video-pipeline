# 数据库配置说明

本项目支持 SQLite（开发/测试）和 PostgreSQL（生产）两种数据库。

## 数据库类型选择

### SQLite（开发/测试环境）
- **优点**: 无需额外安装，开箱即用，适合本地开发
- **缺点**: 不支持并发写入，性能较低
- **配置**: `DATABASE_URL=sqlite+aiosqlite:///data/db/pipeline.db`

### PostgreSQL（生产环境）
- **优点**: 支持并发写入，性能高，支持高级特性（JSONB）
- **缺点**: 需要额外安装和配置
- **配置**: `DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname`

## 环境变量配置

在 `.env` 文件中设置：

```bash
# 开发环境（SQLite）
DATABASE_URL=sqlite+aiosqlite:///data/db/pipeline.db

# 生产环境（PostgreSQL）
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/video_pipeline
```

## 数据库迁移

### SQLite
```bash
cd backend
alembic upgrade head
```

### PostgreSQL
```bash
cd backend
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname alembic upgrade head
```

## 类型兼容性

代码已自动处理两种数据库的类型差异：

| 功能 | SQLite | PostgreSQL |
|------|---------|------------|
| JSON | `sa.JSON` | `postgresql.JSONB` |
| UUID | `sa.UUID` | `postgresql.UUID(as_uuid=True)` |
| 迁移 | 自动检测并选择 | 自动检测并选择 |

## 测试数据库兼容性

运行测试脚本验证数据库兼容性：

```bash
python3 test_db_compatibility.py
```

## 注意事项

1. **迁移文件**: 所有迁移文件都使用动态类型检测，自动适配数据库
2. **模型定义**: 使用 `sa.JSON` 而非 `postgresql.JSONB`，确保兼容性
3. **UUID**: 使用 `postgresql.UUID(as_uuid=True)`，SQLite 会自动降级为 `sa.UUID`
4. **生产部署**: 必须使用 PostgreSQL 以获得最佳性能和并发支持

## 数据库性能对比

| 指标 | SQLite | PostgreSQL |
|--------|---------|------------|
| 并发写入 | ❌ 不支持 | ✅ 支持 |
| JSON 查询 | ⚠️ 基础 | ✅ 高级（JSONB） |
| 连接池 | ❌ 不需要 | ✅ 支持 |
| 事务隔离 | ⚠️ 基础 | ✅ 完整 |
| 适用场景 | 开发/测试 | 生产环境 |

## 迁移到生产数据库

从 SQLite 迁移到 PostgreSQL：

1. 导出 SQLite 数据
2. 创建 PostgreSQL 数据库
3. 运行迁移: `alembic upgrade head`
4. 导入数据
5. 更新 `.env` 中的 `DATABASE_URL`