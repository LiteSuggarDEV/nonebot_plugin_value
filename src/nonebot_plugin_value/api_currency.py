from uuid import uuid4

from nonebot_plugin_orm import AsyncSession

from .models.currency import CurrencyMeta
from .models.currency_pyd import CurrencyData
from .repository import CurrencyRepository


async def list_currencies(session: AsyncSession):
    """获取已存在的货币

    Args:
        session (AsyncSession): 异步Session

    Returns:
        Sequence[CurrencyMeta]: 返回货币列表
    """
    return await CurrencyRepository(session).list_currencies()


async def getcurrency(session: AsyncSession, currency_id: str) -> CurrencyMeta | None:
    """获取一个货币的元信息

    Args:
        session (AsyncSession): SQLAlchemy的异步session
        currency_id (str): 货币唯一ID

    Returns:
        CurrencyMeta | None: 货币元数据（不存在为None）
    """
    return await CurrencyRepository(session).getcurrency(currency_id)


async def get_or_create_currency(
    session: AsyncSession, currency_data: CurrencyData
) -> CurrencyMeta | None:
    """获取或创建新货币（如果存在就获取）

    Args:
        session (AsyncSession): SQLAlchemy的异步session
        currency_data (CurrencyData): 货币元信息

    Returns:
        CurrencyMeta: 货币元信息模型
    """
    if currency_data.currency_id == "":
        while True:
            currency_data.currency_id = uuid4().hex
            if await getcurrency(session, uuid4().hex) is None:
                break
    if (metadata := await getcurrency(session, currency_data.currency_id)) is not None:
        return metadata
    return await CurrencyRepository(session).createcurrency(currency_data)
