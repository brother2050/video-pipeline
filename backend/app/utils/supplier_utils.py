"""
供应商工具函数。
"""

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplier import CapabilityConfig
from app.schemas.enums import SupplierCapability
from app.schemas.supplier import CapabilityConfigResponse, SupplierSlot
from app.suppliers.registry import SupplierRegistry

logger = logging.getLogger(__name__)


async def load_supplier_registry_from_db(
    db: AsyncSession,
    registry: SupplierRegistry | None = None,
) -> SupplierRegistry:
    """
    从数据库加载供应商配置并初始化注册表。
    
    Args:
        db: 数据库会话
        registry: 可选的现有注册表实例，如果未提供则创建新实例
    
    Returns:
        初始化后的供应商注册表
    """
    if registry is None:
        registry = SupplierRegistry()
    
    result = await db.execute(select(CapabilityConfig))
    configs = result.scalars().all()
    
    if not configs:
        logger.warning("No supplier configurations found in database")
        return registry
    
    schema_configs = []
    for config in configs:
        try:
            capability = SupplierCapability(config.capability)
            schema_configs.append(
                CapabilityConfigResponse(
                    capability=capability,
                    suppliers=[SupplierSlot(**s) for s in config.suppliers],
                    retry_count=config.retry_count,
                    timeout_seconds=config.timeout_seconds,
                    local_timeout_seconds=config.local_timeout_seconds,
                )
            )
        except ValueError:
            logger.warning(f"Unknown capability: {config.capability}, skipping")
    
    if schema_configs:
        await registry.initialize(schema_configs)
        logger.info(f"Supplier registry initialized with {len(schema_configs)} capabilities")
    else:
        logger.warning("No valid supplier configurations found")
    
    return registry