# 事件预处理/后处理钩子
import asyncio
from collections.abc import Awaitable, Callable

from nonebot import logger

from .context import TransactionComplete, TransactionContext
from .exception import BasicException
from .hooks_type import HooksType


class HooksManager:
    __hooks: dict[str, list[Callable[..., Awaitable[None]]]]
    _instance = None

    def __new__(cls):
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
        if all(hook_name != hook.value for hook in HooksType.__members__.values()):
            raise ValueError(f"Invalid hook name: {hook_name}")
        self.__hooks.setdefault(hook_name, []).append(hook_func)

    async def run_hooks(
        self, hook_name: str, context: TransactionComplete | TransactionContext
    ) -> None:
        if (hooks := self.__hooks.get(hook_name)) is None:
            return

        async def _run_single_hook(hook: Callable[..., Awaitable[None]]) -> None:
            try:
                await hook(context)
            except BasicException:
                raise
            except Exception as e:
                logger.opt(exception=e).error("钩子执行失败")

        rst: list[BaseException | None] = await asyncio.gather(
            *[_run_single_hook(hook) for hook in hooks], return_exceptions=True
        )  # 即使没用gather的先前实现，遇到exception中断也会抛出异常，此处只是优化性能。
        for i in rst:
            if i is not None:
                raise i
