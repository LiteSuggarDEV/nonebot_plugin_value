from __future__ import annotations

import enum
from asyncio import Lock
from collections import OrderedDict
from collections.abc import Hashable
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Generic, TypeVar

from typing_extensions import Self

from .pyd_models.balance_pyd import UserAccountData
from .pyd_models.base_pyd import BaseData
from .pyd_models.currency_pyd import CurrencyData
from .pyd_models.transaction_pyd import TransactionData


class CacheCategoryEnum(str, enum.Enum):
    CURRENCY = "currency"
    ACCOUNT = "account"
    TRANSACTION = "transaction"


T = TypeVar("T", BaseData, CurrencyData, TransactionData, UserAccountData)


@dataclass
class Cache(Generic[T]):
    """Cache存储模型"""

    # 默认缓存最大条目数
    max_size: int = 1000

    # LRU实现
    _cache: OrderedDict[str, BaseData] = field(default_factory=lambda: OrderedDict())

    def __post_init__(self):
        if self.max_size <= 0:
            self.max_size = 1000

    async def update(self, *, data: BaseData) -> bool:
        data_id = data.uni_id if isinstance(data, UserAccountData) else data.id
        async with self._lock(data_id):
            if existing := self._cache.get(data_id):
                existing.model_validate(data, from_attributes=True)
                self._cache.move_to_end(data_id)
                return True

            # 添加新数据
            self._cache[data_id] = data
            self._cache.move_to_end(data_id)

            # 如果超出最大大小，删除最久未使用的项（第一个）
            if len(self._cache) > self.max_size:
                self._cache.popitem(last=False)

            return False

    async def get(self, *, data_id: str) -> BaseData | None:
        async with self._lock(data_id):
            item = self._cache.get(data_id)
            if item is not None:
                # 访问后移到末尾（标记为最近使用）
                self._cache.move_to_end(data_id)
            return item

    async def get_all(self) -> list[BaseData]:
        async with self._lock():
            # 返回所有缓存项的副本
            return list(self._cache.values())

    async def delete(self, *, data_id: str):
        async with self._lock(data_id):
            self._cache.pop(data_id, None)

    async def clear(self):
        async with self._lock(0):
            self._cache.clear()

    @staticmethod
    @lru_cache(1024)
    def _lock(*args: Hashable) -> Lock:
        return Lock()


class CacheManager:
    _instance = None
    _cached: dict[CacheCategoryEnum, Cache[Any]]

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._cached = {}
        return cls._instance

    async def get_cache(
        self, category: CacheCategoryEnum, max_size: int = 1000
    ) -> Cache[Any]:
        # 为不同类别创建具有不同大小的缓存
        if category not in self._cached:
            self._cached[category] = Cache(max_size=max_size)
        return self._cached[category]

    async def update_cache(
        self,
        *,
        category: CacheCategoryEnum,
        data: BaseData,
        max_size: int = 1000,
    ) -> Self:
        """更新缓存

        Args:
            category (CacheCategoryEnum): 缓存板块
            data (BaseData): 数据
            max_size (int): 缓存最大大小
        """
        async with self._get_lock(category):
            cache = await self.get_cache(category, max_size)
            await cache.update(data=data)
        return self

    async def expire_cache(
        self, *, category: CacheCategoryEnum, data_id: str | None = None
    ) -> Self:
        """使缓存过期(当数据库操作中该条删除时使用)

        Args:
            category (CacheCategoryEnum): 缓存板块
            data_id (str | None, optional): 数据ID. Defaults to None.
        """
        async with self._get_lock(category):
            if category in self._cached:
                if data_id is not None:
                    cache = await self.get_cache(category)
                    await cache.delete(data_id=data_id)
                else:
                    self._cached.pop(category, None)
        return self

    async def expire_all_cache(self) -> Self:
        """使所有缓存过期"""

        self._cached.clear()
        return self

    @staticmethod
    @lru_cache(1024)
    def _get_lock(*args: Hashable) -> Lock:
        return Lock()
