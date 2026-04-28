# 数据库配置说明

本项目使用 PostgreSQL 作为数据库。

## 数据库配置

### PostgreSQL（生产环境）
- **优点**: 支持并发写入，性能高，支持高级特性（JSONB）
- **配置**: `DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname`

## 环境变量配置

在 `.env` 文件中设置：

```bash
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/video_pipeline
```

## 数据库迁移

```bash
cd backend
alembic upgrade head
```

## 数据库特性

| 功能 | PostgreSQL |
|------|------------|
| JSON | `postgresql.JSONB` |
| UUID | `postgresql.UUID(as_uuid=True)` |
| 迁移 | 自动检测并选择 |

## 注意事项

1. **迁移文件**: 所有迁移文件都使用 PostgreSQL 类型
2. **模型定义**: 使用 `postgresql.JSONB` 和 `postgresql.UUID(as_uuid=True)`
3. **连接池**: 支持 `pool_size` 和 `max_overflow` 参数
4. **生产部署**: 必须使用 PostgreSQL 以获得最佳性能和并发支持

## 数据库性能

| 指标 | PostgreSQL |
|--------|------------|
| 并发写入 | ✅ 支持 |
| JSON 查询 | ✅ 高级（JSONB） |
| 连接池 | ✅ 支持 |
| 事务隔离 | ✅ 完整 |
| 适用场景 | 生产环境 |

## 数据库初始化

### 1. 创建数据库

```bash
# 使用 psql 创建数据库
createdb videopipeline

# 或者使用 SQL 命令
psql -U postgres
CREATE DATABASE videopipeline;
\q
```

### 2. 运行迁移

```bash
cd backend
alembic upgrade head
```

### 3. 验证连接

```bash
# 测试数据库连接
psql -U user -d videopipeline

# 查看表
\dt

# 退出
\q
```

## 数据库备份与恢复

### 备份

```bash
# 备份数据库
pg_dump -U user -d videopipeline > backup.sql

# 备份为压缩文件
pg_dump -U user -d videopipeline | gzip > backup.sql.gz
```

### 恢复

```bash
# 恢复数据库
psql -U user -d videopipeline < backup.sql

# 恢复压缩文件
gunzip -c backup.sql.gz | psql -U user -d videopipeline
```

## 常见问题

### Q1: 连接数据库失败

检查以下几点：
1. PostgreSQL 服务是否运行
2. 用户名和密码是否正确
3. 数据库是否存在
4. 端口是否正确（默认 5432）

### Q2: 权限不足

确保用户有足够的权限：

```sql
-- 授予所有权限
GRANT ALL PRIVILEGES ON DATABASE videopipeline TO user;

-- 授予 schema 权限
GRANT ALL ON SCHEMA public TO user;
```

### Q3: 连接池耗尽

调整连接池配置：

```python
# 在 database.py 中调整
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=20,  # 增加连接池大小
    max_overflow=40,  # 增加最大溢出连接数
)
```