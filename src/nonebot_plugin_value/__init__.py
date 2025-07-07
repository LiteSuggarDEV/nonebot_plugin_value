from nonebot import get_driver
from nonebot.plugin import PluginMetadata, require

require("nonebot_plugin_orm")

from . import action_type, repository
from .db_api import api_balance, api_currency, api_transaction
from .db_api.api_currency import get_or_create_currency
from .hook import context, exception, hooks_manager, hooks_type
from .models import currency, currency_pyd
from .models.currency_pyd import CurrencyData
from .repository import DEFAULT_CURRENCY_UUID

__plugin_meta__ = PluginMetadata(
    name="Value",
    description="通用经济API插件",
    usage="请查看API文档。",
    type="library",
    homepage="https://github.com/JohnRichard4096/nonebot_plugin_value",
)

__all__ = [
    "action_type",
    "api_balance",
    "api_currency",
    "api_transaction",
    "context",
    "currency",
    "currency_pyd",
    "exception",
    "hook",
    "hooks_manager",
    "hooks_type",
    "repository",
]


@get_driver().on_startup
async def init_db():
    """
    初始化数据库
    """
    await get_or_create_currency(
        CurrencyData(id=DEFAULT_CURRENCY_UUID.hex),
    )
