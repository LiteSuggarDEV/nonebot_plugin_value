from ..db_api.currency import get_default_currency as _default_currency
from ..db_api.currency import get_or_create_currency as _create_currency
from ..db_api.currency import getcurrency as _g_currency
from ..db_api.currency import list_currencies as _currencies
from ..db_api.currency import remove_currency as _remove_currency
from ..db_api.currency import update_currency as _update_currency
from ..pyd_models.currency_pyd import CurrencyData


async def update_currency(currency_data: CurrencyData) -> CurrencyData:
    """更新货币信息

    Args:
        currency_data (CurrencyData): 货币数据

    Returns:
        CurrencyData: 货币数据
    """
    currency = await _update_currency(currency_data)
    return CurrencyData.model_validate(currency)


async def remove_currency(currency_id: str):
    """删除一个货币（警告！这是一个及其危险的操作！这会删除所有关联的账户！）

    Args:
        currency_id (str): 货币唯一ID

    Returns:
        bool: 是否删除成功
    """
    await _remove_currency(currency_id)

async def list_currencies() -> list[CurrencyData]:
    """获取所有已存在货币

    Returns:
        list[CurrencyData]: 包含所有已存在货币的列表
    """
    currencies = await _currencies()
    return [CurrencyData.model_validate(currency) for currency in currencies]

async def get_currency(currency_id: str) -> CurrencyData | None:
    """获取一个货币信息

    Args:
        currency_id (str): 货币唯一ID

    Returns:
        CurrencyData | None: 货币数据，如果不存在则返回None
    """
    currency = await _g_currency(currency_id)
    if currency is None:
        return None
    return CurrencyData.model_validate(currency)

async def get_default_currency() -> CurrencyData:
    """获取默认货币的信息

    Returns:
        CurrencyData: 货币信息
    """
    currency = await _default_currency()
    return CurrencyData.model_validate(currency)

async def create_currency(currency_data: CurrencyData) -> CurrencyData:
    """创建货币

    Args:
        currency_data (CurrencyData): 货币数据

    Returns:
        CurrencyData: 货币数据
    """
    currency = await _create_currency(currency_data)
    return CurrencyData.model_validate(currency)
