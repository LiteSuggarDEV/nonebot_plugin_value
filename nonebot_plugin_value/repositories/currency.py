# Repository,更加底层的数据库操作接口
from collections.abc import Sequence

from nonebot import logger
from nonebot_plugin_orm import AsyncSession
from sqlalchemy import delete, select, update

from ..exception import (
    CurrencyNotFound,
)
from ..models.currency import CurrencyMeta
from ..pyd_models.currency_pyd import CurrencyData


class CurrencyRepository:
    """货币元数据操作"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_currency(self, currency_id: str) -> CurrencyMeta | None:
        """获取货币信息"""
        session = self.session
        result = await self.session.execute(
            select(CurrencyMeta).where(CurrencyMeta.id == currency_id)
        )
        if currency_meta := result.scalar_one_or_none():
            session.add(currency_meta)
            return currency_meta
        return None

    async def get_currency_by_kwargs(self, **kwargs: object) -> CurrencyMeta | None:
        """获取货币信息"""
        session = self.session
        result = await session.execute(
            select(CurrencyMeta).where(
                *(
                    getattr(CurrencyMeta, key) == value
                    for key, value in kwargs.items()
                    if hasattr(CurrencyMeta, key)
                )
            )
        )
        if currency_meta := result.scalar_one_or_none():
            session.add(currency_meta)
            return currency_meta
        return None

    async def get_or_create_currency(
        self, currency_data: CurrencyData
    ) -> tuple[CurrencyMeta, bool]:
        """获取或创建货币"""
        session = self.session
        stmt = await session.execute(
            select(CurrencyMeta).where(
                CurrencyMeta.id == currency_data.id,
            )
        )
        if (currency := stmt.scalars().first()) is not None:
            session.add(currency)
            return currency, True
        result = await self.createcurrency(currency_data)
        return result, False

    async def createcurrency(self, currency_data: CurrencyData) -> CurrencyMeta:
        """创建新货币"""
        session = self.session
        currency = CurrencyMeta(**currency_data.model_dump())
        session.add(currency)
        await session.commit()
        await session.refresh(currency)
        return currency

    async def update_currency(self, currency_data: CurrencyData) -> CurrencyMeta:
        """更新货币信息"""
        session = self.session

        # 明确指定要更新的字段，避免包含不需要的字段（如 id, created_at 等）
        update_values = {
            "display_name": currency_data.display_name,
            "symbol": currency_data.symbol,
            "default_balance": currency_data.default_balance,
            "allow_negative": currency_data.allow_negative,
        }

        stmt = (
            update(CurrencyMeta)
            .where(CurrencyMeta.id == currency_data.id)
            .values(**update_values)
        )
        await session.execute(stmt)
        await session.flush()  # 先 flush 确保更新生效

        # 重新查询获取最新数据
        stmt = (
            select(CurrencyMeta)
            .where(CurrencyMeta.id == currency_data.id)
            .with_for_update()
        )
        result = await session.execute(stmt)
        currency_meta = result.scalar_one()
        session.add(currency_meta)
        return currency_meta

    async def list_currencies(self) -> Sequence[CurrencyMeta]:
        """列出所有货币"""
        session = self.session
        result = await self.session.execute(select(CurrencyMeta))
        data = result.scalars().all()
        session.add_all(data)
        return data

    async def remove_currency(self, currency_id: str):
        """删除货币（警告！会同时删除所有关联账户！）"""
        session = self.session
        currency = (
            await session.execute(
                select(CurrencyMeta)
                .where(CurrencyMeta.id == currency_id)
                .with_for_update()
            )
        ).scalar()
        if currency is None:
            raise CurrencyNotFound(f"Currency {currency_id} not found")

        logger.warning(f"Deleting currency {currency_id}")
        stmt = delete(CurrencyMeta).where(CurrencyMeta.id == currency_id)
        await session.execute(stmt)
