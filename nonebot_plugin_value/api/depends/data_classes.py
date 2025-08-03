from dataclasses import dataclass, field

from nonebot.adapters import Event

from ...uuid_lib import DEFAULT_CURRENCY_UUID, to_uuid
from ..api_balance import UserAccountData, get_or_create_account
from ..api_currency import CurrencyData, get_currency, get_default_currency
from ..api_transaction import (
    TransactionData,
    get_transaction_history,
    get_transaction_history_by_time_range,
)


@dataclass
class TransactionHistory:
    limit: int
    timerange: tuple[float, float] | None = field(default=None)

    async def __call__(self, event: Event) -> list[TransactionData]:
        if self.timerange is None:
            return await get_transaction_history(
                to_uuid(event.get_user_id()), self.limit
            )
        start_time, end_time = self.timerange
        return await get_transaction_history_by_time_range(
            to_uuid(event.get_user_id()), start_time, end_time, self.limit
        )


@dataclass
class Account:
    currency_id: str | None = field(default=None)

    async def __call__(self, event: Event) -> UserAccountData:
        if self.currency_id is None:
            self.currency_id = DEFAULT_CURRENCY_UUID.hex
        return await get_or_create_account(
            to_uuid(event.get_user_id()), self.currency_id
        )


@dataclass
class Currency:
    c_id: str | None

    async def __call__(self) -> CurrencyData | None:
        if self.c_id is None:
            return await get_default_currency()
        return await get_currency(self.c_id)
