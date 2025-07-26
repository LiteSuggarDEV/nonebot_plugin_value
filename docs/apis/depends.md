# EconomyValue-依赖注入模式 API 文档

> **本质为 [标准 API](./standard.md) 的二次封装，用于依赖注入**

## `~.api.depends.factory`

> **依赖注入模式工厂**

```python
class DependsSwitch:
    @staticmethod
    def account_data(
        *,
        currency_id: str | None = None,
    ) -> Callable[..., Awaitable[UserAccountData]]:
        """获得账户数据

        Args:
            currency_id (str | None, optional): 货币ID. Defaults to None.

        Returns:
            Callable[..., Awaitable[UserAccountData]]: 可供NoneBot调用的依赖函数类
        """
        ...

    @staticmethod
    def currency_data(
        *,
        currency_id: str | None = None,
    ) -> Callable[..., Awaitable[CurrencyData | None]]:
        """
        获取货币数据依赖函数

        Args:
            currency_id (str | None, optional): 货币ID. Defaults to None.

        Returns:
            Callable[..., Awaitable[CurrencyData | None]]: 可供NoneBot调用的依赖函数类
        """
        ...

    @staticmethod
    def transaction_data(
        *,
        limit: int = 10,
        timerange: tuple[float, float] | None = None,
    ) -> Callable[..., Awaitable[list[TransactionData]]]:
        """
        获取交易记录

        Args:
            limit (int, optional): 交易记录数量限制. Defaults to 10.
            timerange (tuple[float, float] | None, optional): 时间范围. Defaults to None.

        Returns:
            Callable[..., Awaitable[list[TransactionData]]]: 可供NoneBot调用的依赖函数类
        """
        ...

    @staticmethod
    def account_executor(
        *,
        currency_id: str | None = None,
    ) -> Callable[..., Awaitable[AccountExecutor]]:
        """
        Args:
            currency_id (str | None, optional): 货币ID. Defaults to None.

        Returns:
            Callable[..., Awaitable[AccountExecutor]]: 账号数据操作对象
        """
        ...

```

## 示例使用

```python
from nonebot import on_command, require
from nonebot.adapters import Event
from nonebot.params import Depends

require("nonebot_plugin_value")
from nonebot_plugin_value.api.depends.factory import DependsSwitch, UserAccountData

test = on_command("test")


@test.handle()
async def _(user_data: UserAccountData = Depends(DependsSwitch.account_data())):
    await test.finish(user_data.balance)
```
