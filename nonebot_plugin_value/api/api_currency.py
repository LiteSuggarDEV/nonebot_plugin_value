from nonebot_plugin_orm import get_session

from ..pyd_models.currency_pyd import CurrencyData
from ..services.currency import create_currency as _create_currency
from ..services.currency import get_currency as _g_currency
from ..services.currency import get_currency_by_kwargs as __currency_by_kwargs
from ..services.currency import get_default_currency as _default_currency
from ..services.currency import get_or_create_currency as _get_or_create_currency
from ..services.currency import list_currencies as _currencies
from ..services.currency import remove_currency as _remove_currency
from ..services.currency import update_currency as _update_currency


async def update_currency(currency_data: CurrencyData) -> CurrencyData:
    """更新货币信息

    Args:
        currency_data (CurrencyData): 货币数据

    Returns:
        CurrencyData: 货币数据
    """
    async with get_session() as session:
        currency = await _update_currency(currency_data, session)
        return CurrencyData.model_validate(currency, from_attributes=True)


async def remove_currency(currency_id: str) -> None:
    """删除一个货币（警告！这是一个及其危险的操作！这会删除所有关联的账户！）

    Args:
        currency_id (str): 货币唯一ID
    """

    await _remove_currency(currency_id)


async def list_currencies() -> list[CurrencyData]:
    """获取所有已存在货币

    Returns:
        list[CurrencyData]: 包含所有已存在货币的列表
    """
    async with get_session() as session:
        currencies = await _currencies(session)
        return [
            CurrencyData.model_validate(currency, from_attributes=True)
            for currency in currencies
        ]

async def get_currency(currency_id: str) -> CurrencyData | None:
    """获取一个货币信息

    Args:
        currency_id (str): 货币唯一ID

    Returns:
        CurrencyData | None: 货币数据，如果不存在则返回None
    """
    async with get_session() as session:
        currency = await _g_currency(currency_id, session)
        if currency is None:
            return None
        return CurrencyData.model_validate(currency, from_attributes=True)


async def get_currency_by_kwargs(**kwargs: object) -> CurrencyData | None:
    """获取一个货币信息

    Args:
        **kwargs (object): 通过货币属性联合查询获取货币信息

    Returns:
        CurrencyData | None: 货币数据，如果不存在则返回None
    """
    async with get_session() as session:
        currency = await __currency_by_kwargs(**kwargs, session=session)
        if currency is None:
            return None
        return CurrencyData.model_validate(currency, from_attributes=True)


async def get_default_currency() -> CurrencyData:
    """获取默认货币的信息

    Returns:
        CurrencyData: 货币信息
    """
    async with get_session() as session:
        currency = await _default_currency(session)
        return CurrencyData.model_validate(currency, from_attributes=True)


async def create_currency(currency_data: CurrencyData) -> None:
    """创建新货币

    Args:
        currency_data (CurrencyData): 货币信息

    Returns:
        CurrencyData: 货币信息
    """
    async with get_session() as session:
        await _create_currency(currency_data, session)


async def get_or_create_currency(currency_data: CurrencyData) -> CurrencyData:
    """获取或者创建货币（一般在初始化时使用）

    Args:
        currency_data (CurrencyData): 货币数据

    Returns:
        CurrencyData: 货币数据
    """
    async with get_session() as session:
        currency, _ = await _get_or_create_currency(currency_data, session)
        return CurrencyData.model_validate(currency, from_attributes=True)
