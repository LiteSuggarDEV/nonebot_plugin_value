from dataclasses import dataclass, field

from nonebot.adapters import Event
from typing_extensions import Self

from ..uuid_lib import to_uuid
from .api_balance import (
    UserAccountData,
    add_balance,
    del_balance,
    get_or_create_account,
)
from .api_currency import get_default_currency


@dataclass
class AccountExecutor:
    currency_id: str | None = field(default=None)
    user_id: str = field(default="")
    data_map: dict[str, UserAccountData] = field(default_factory=lambda: {})

    async def __call__(self, event: Event) -> Self:
        self.user_id = to_uuid(event.get_user_id())
        if self.currency_id is None:
            currency_id = (await get_default_currency()).id
        else:
            currency_id = self.currency_id
        self.data_map[currency_id] = await get_or_create_account(
            self.user_id, currency_id
        )
        return self

    async def get_data(self, currency_id: str | None = None) -> UserAccountData:
        """获取账号数据

        Args:
            currency_id (str | None, optional): 货币ID. Defaults to None.

        Returns:
            UserAccountData: 账号数据
        """
        currency_id = currency_id or self.currency_id
        assert currency_id is not None, "Currency ID is required"
        return self.data_map.get(
            currency_id,
            await get_or_create_account(self.user_id, currency_id),
        )

    async def get_balance(
        self,
        currency_id: str | None = None,
    ) -> float:
        """获取账号余额

        Args:
            currency_id (str | None, optional): 货币ID. Defaults to None.

        Returns:
            float: 余额
        """
        return (await self.get_data(currency_id)).balance

    async def add_balance(
        self,
        amount: float,
        currency_id: str | None = None,
        source: str = "_transfer SYS",
    ) -> Self:
        """添加账号余额

        Args:
            amount (float): 大小（>0）
            currency_id (str | None, optional): 货币ID. Defaults to None.
            source (str, optional): 源. Defaults to "_transfer SYS".

        Returns:
            Self: Self
        """
        currency_id = currency_id or self.currency_id
        assert currency_id is not None, "Currency ID is required"
        self.data_map[currency_id] = await add_balance(
            self.user_id,
            amount,
            source,
            currency_id,
        )
        return self

    async def decrease_balance(
        self,
        amount: float,
        currency_id: str | None = None,
        source: str = "_transfer SYS",
    ) -> Self:
        """减少余额

        Args:
            amount (float): 大小（>0）
            currency_id (str | None, optional): 货币ID. Defaults to None.
            source (str, optional): 源. Defaults to "_transfer SYS".

        Returns:
            Self: Self
        """
        currency_id = currency_id or self.currency_id
        assert currency_id is not None, "Currency ID is required"
        self.data_map[currency_id] = await del_balance(
            self.user_id,
            amount,
            source,
            currency_id,
        )
        return self
