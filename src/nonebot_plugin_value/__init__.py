from nonebot.plugin import PluginMetadata, require

require("nonebot_plugin_orm")
from . import api_balance, hook, repository
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
    "context",
    "currency",
    "currency_pyd",
    "exception",
    "hook",
    "hooks_manager",
    "hooks_type",
    "repository",
]
