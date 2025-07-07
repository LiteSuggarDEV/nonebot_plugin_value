from nonebot import get_driver
from nonebot.plugin import PluginMetadata, require

require("nonebot_plugin_orm")
from nonebot_plugin_orm import get_session

from . import api_balance, api_currency, api_transaction, hook, repository
from .api_currency import get_or_create_currency
from .hook import context, exception, hooks_manager, hooks_type
from .models import currency, currency_pyd

__plugin_meta__ = PluginMetadata(
    name="Value",
    description="通用经济API插件",
    usage="请查看API文档。",
    type="library",
    homepage="https://github.com/JohnRichard4096/nonebot_plugin_value",
)

__all__ = [
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
    async with get_session() as session:
        await get_or_create_currency(session, currency_pyd.CurrencyData())
