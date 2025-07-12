from collections.abc import Sequence
from uuid import uuid4

from nonebot_plugin_orm import AsyncSession, get_session

from ..models.currency import CurrencyMeta
from ..pyd_models.currency_pyd import CurrencyData
from ..repository import DEFAULT_CURRENCY_UUID, CurrencyRepository


async def update_currency(
    currency_data: CurrencyData,
    session: AsyncSession,
) -> CurrencyMeta:
    """更新一个货币

    Args:
        currency_data (CurrencyData): 货币元信息
        session (AsyncSession): 异步Session. Defaults to None.

    Returns:
        CurrencyMeta: 货币元信息模型
    """
    async with session:
        return await CurrencyRepository(session).update_currency(currency_data)


async def remove_currency(currency_id: str) -> None:
    """删除一个货币(警告！会移除关联账户！)

    Args:
        currency_id (str): 货币ID
        session (AsyncSession ): 异步Session.
    """

    session = get_session()
    async with session:
        await CurrencyRepository(session).remove_currency(currency_id)


async def list_currencies(session: AsyncSession) -> Sequence[CurrencyMeta]:
    """获取已存在的货币

    Args:
        session (AsyncSession): 异步Session

    Returns:
        Sequence[CurrencyMeta]: 返回货币列表
    """
    async with session:
        data = await CurrencyRepository(session).list_currencies()
        return data


async def getcurrency(currency_id: str, session: AsyncSession) -> CurrencyMeta | None:
    """获取一个货币的元信息

    Args:
        session (AsyncSession): SQLAlchemy的异步session
        currency_id (str): 货币唯一ID

    Returns:
        CurrencyMeta | None: 货币元数据（不存在为None）
    """
    async with session:
        metadata = await CurrencyRepository(session).getcurrency(currency_id)
        return metadata


async def get_or_create_currency(
    currency_data: CurrencyData,
    session: AsyncSession,
) -> tuple[CurrencyMeta, bool]:
    """获取或创建新货币（如果存在就获取）

    Args:
        session (AsyncSession): SQLAlchemy的异步session
        currency_data (CurrencyData): 货币元信息

    Returns:
        tuple[CurrencyMeta, bool] 元数据和是否创建
    """
    async with session:
        if currency_data.id == "":
            while True:
                currency_data.id = uuid4().hex
                if (
                    await getcurrency(
                        uuid4().hex,
                        session,
                    )
                    is None
                ):
                    break
        if (
            metadata := await getcurrency(
                currency_data.id,
                session,
            )
        ) is not None:
            return metadata, False
        else:
            metadata = await CurrencyRepository(session).createcurrency(currency_data)
            return metadata, True


async def get_default_currency(session: AsyncSession) -> CurrencyMeta:
    """获取默认货币

    Args:
        session (AsyncSession | None, optional): 异步会话. Defaults to None.

    Returns:
        CurrencyMeta: 货币元数据
    """
    async with session:
        return (
            await get_or_create_currency(
                CurrencyData(id=DEFAULT_CURRENCY_UUID.hex), session
            )
        )[0]
