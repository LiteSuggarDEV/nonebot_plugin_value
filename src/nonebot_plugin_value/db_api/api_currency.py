from uuid import uuid4

from nonebot_plugin_orm import AsyncSession, get_session

from ..models.currency import CurrencyMeta
from ..models.currency_pyd import CurrencyData
from ..repository import DEFAULT_CURRENCY_UUID, CurrencyRepository


async def list_currencies(session: AsyncSession | None = None):
    """获取已存在的货币

    Args:
        session (AsyncSession): 异步Session

    Returns:
        Sequence[CurrencyMeta]: 返回货币列表
    """
    if session is None:
        session = get_session()
    async with session:
        data = await CurrencyRepository(session).list_currencies()
        return data


async def getcurrency(
    currency_id: str, session: AsyncSession | None = None
) -> CurrencyMeta | None:
    """获取一个货币的元信息

    Args:
        session (AsyncSession): SQLAlchemy的异步session
        currency_id (str): 货币唯一ID

    Returns:
        CurrencyMeta | None: 货币元数据（不存在为None）
    """
    if session is None:
        session = get_session()
    async with session:
        metadata = await CurrencyRepository(session).getcurrency(currency_id)
        return metadata


async def get_or_create_currency(
    currency_data: CurrencyData,
    session: AsyncSession | None = None,
) -> tuple[CurrencyMeta, bool]:
    """获取或创建新货币（如果存在就获取）

    Args:
        session (AsyncSession): SQLAlchemy的异步session
        currency_data (CurrencyData): 货币元信息

    Returns:
        tuple[CurrencyMeta, bool] 元数据和是否创建
    """
    if session is None:
        session = get_session()
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
    """获取默认货币"""
    async with session:
        return (
            await get_or_create_currency(
                CurrencyData(id=DEFAULT_CURRENCY_UUID.hex), session
            )
        )[0]
