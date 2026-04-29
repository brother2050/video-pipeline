"""
数据库连接模块。
支持 PostgreSQL（生产）。
"""

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config import settings


class Base(DeclarativeBase):
    """所有模型的基类"""
    pass


@lru_cache
def _get_engine():
    """
    懒加载创建数据库引擎。
    使用lru_cache确保每个fork出来的worker进程只创建一次Engine，
    使用NullPool避免连接绑定到已关闭的event loop。
    """
    return create_async_engine(
        settings.database_url,
        echo=settings.debug,
        poolclass=NullPool,
    )


def get_async_session_factory():
    """
    获取异步session factory。
    确保引擎在async上下文中创建。
    """
    engine = _get_engine()
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async_session_factory = get_async_session_factory()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：提供数据库 session，自动关闭"""
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """启动时创建所有表（开发用，生产用 Alembic）"""
    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """关闭时释放连接池"""
    engine = _get_engine()
    await engine.dispose()