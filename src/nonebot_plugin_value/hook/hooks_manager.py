# 事件预处理/后处理钩子
from collections.abc import Awaitable, Callable
from typing import Any

from nonebot import logger

from .context import BasicModel
from .exception import CancelAction
from .hooks_type import HooksType


class HooksManager:
    __hooks: dict[str, list[Callable[..., Awaitable[None]]]]
    _instance = None

    def __new__(cls, *args: Any, **kwargs: Any):
        """重写 __new__ 方法实现单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__hooks = {}
        return cls._instance

    def on_event(self, hook_name: str):
        """修饰器式的注册方法

        Args:
            hook_name (str): 事件名称
        """

        def decorator(func: Callable[..., Awaitable[None]]):
            # 直接复用现有注册逻辑
            self.register(hook_name, func)
            return func  # 返回原函数保持装饰器特性

        return decorator

    def register(
        self, hook_name: str, hook_func: Callable[..., Awaitable[None]]
    ) -> None:
        """注册一个Hook"""
        if not HooksType.valid_hooks(hook_name):
            raise ValueError(f"Invalid hook name: {hook_name}")
        self.__hooks.setdefault(hook_name, []).append(hook_func)

    async def run_hooks(self, hook_name: str, context: BasicModel) -> None:
        if (hooks := self.__hooks.get(hook_name)) is None:
            return

        async def _run_single_hook(hook: Callable[..., Awaitable[None]]) -> None:
            try:
                await hook(context)
            except CancelAction:
                raise
            except Exception:
                logger.opt(exception=True).error("钩子执行失败")

        for hook in hooks:
            await _run_single_hook(hook)
