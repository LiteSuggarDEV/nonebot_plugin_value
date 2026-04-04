import contextlib
from collections.abc import Sequence

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
        session (AsyncSession): 异步 Session

    Returns:
        CurrencyMeta: 货币元信息模型
    """
    return await CurrencyRepository(session).update_currency(currency_data)


async def remove_currency(
    currency_id: str, session: AsyncSession | None = None
) -> None:
    """删除一个货币(警告！会移除关联账户！)

    Args:
        currency_id (str): 货币ID
        session (AsyncSession | None, optional): 异步Session. Defaults to None.
    """

    arg_session = session
    session = session or get_session()
    async with session if arg_session is None else contextlib.nullcontext():
        await CurrencyRepository(session).remove_currency(currency_id)
        if not arg_session:
            await session.commit()


async def list_currencies(
    session: AsyncSession,
) -> Sequence[CurrencyMeta]:
    """获取已存在的货币

    Args:
        session (AsyncSession): 异步 Session

    Returns:
        Sequence[CurrencyMeta]: 返回货币列表
    """
    return await CurrencyRepository(session).list_currencies()


async def get_currency(
    currency_id: str,
    session: AsyncSession,
) -> CurrencyMeta | None:
    """获取一个货币的元信息

    Args:
        currency_id (str): 货币唯一 ID
        session (AsyncSession): SQLAlchemy 的异步 session

    Returns:
        CurrencyMeta | None: 货币元数据（不存在为 None）
    """

    return await CurrencyRepository(session).get_currency(currency_id)


async def get_currency_by_kwargs(
    session: AsyncSession,
    **kwargs: object,
) -> CurrencyMeta | None:
    """获取一个货币的元信息

    Args:
        session (AsyncSession): SQLAlchemy 的异步 session
        **kwargs (object): 查询条件（货币属性字段）

    Returns:
        CurrencyMeta | None: 货币元数据（不存在为 None）
    """

    return await CurrencyRepository(session).get_currency_by_kwargs(**kwargs)


async def create_currency(
    currency_data: CurrencyData, session: AsyncSession | None = None
) -> CurrencyMeta:
    """创建货币

    Args:
        currency_data (CurrencyData): 货币数据
        session (AsyncSession | None, optional): SQLAlchemy 的异步 session. Defaults to None.

    Returns:
        CurrencyMeta: 创建的货币元数据
    """
    arg_session = session
    session = session or get_session()
    async with session if arg_session is None else contextlib.nullcontext():
        result = await CurrencyRepository(session).createcurrency(currency_data)
        if not arg_session:
            await session.commit()
        return result


async def get_or_create_currency(
    currency_data: CurrencyData,
    session: AsyncSession,
) -> tuple[CurrencyMeta, bool]:
    """获取或创建新货币（如果存在就获取）

    Args:
        currency_data (CurrencyData): 货币元信息
        session (AsyncSession): SQLAlchemy 的异步 session

    Returns:
        tuple[CurrencyMeta, bool]: 元数据和是否创建
    """

    repo = CurrencyRepository(session)
    return await repo.get_or_create_currency(currency_data)


async def get_default_currency(session: AsyncSession) -> CurrencyMeta:
    """获取默认货币

    Args:
        session (AsyncSession): 异步会话

    Returns:
        CurrencyMeta: 货币元数据
    """

    return (
        await get_or_create_currency(
            CurrencyData(id=DEFAULT_CURRENCY_UUID.hex), session
        )
    )[0]
