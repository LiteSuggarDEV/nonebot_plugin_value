from collections.abc import Awaitable, Callable
from typing import Any

from ...pyd_models.balance_pyd import UserAccountData
from ...pyd_models.currency_pyd import CurrencyData
from ...pyd_models.transaction_pyd import TransactionData
from ...uuid_lib import DEFAULT_CURRENCY_UUID
from ..executor import AccountExecutor
from .data_classes import Account, Currency, TransactionHistory


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
        return Account(currency_id)

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
        return Currency(currency_id)

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
        return TransactionHistory(limit, timerange)

    @staticmethod
    def account_executor(
        *,
        currency_id: str = DEFAULT_CURRENCY_UUID.hex,
        **kwargs: Any,
    ) -> Callable[..., Awaitable[AccountExecutor]]:
        """
        Args:
            currency_id (str | None, optional): 货币ID. Defaults to None.

        Returns:
            Callable[..., Awaitable[AccountExecutor]]: 账号数据操作对象
        """
        return AccountExecutor(currency_id=currency_id, **kwargs)
