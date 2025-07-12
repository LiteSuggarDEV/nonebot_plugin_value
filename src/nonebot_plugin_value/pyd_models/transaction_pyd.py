from datetime import datetime, timezone

from pydantic import Field

from .base_pyd import BaseData


class TransactionData(BaseData):
    id: str = Field(default="")
    account_id: str = Field(default="")
    currency_id: str = Field(default="")
    amount: float = Field(default=0.0)
    action: str = Field(default="")
    source: str = Field(default="")
    balance_before: float = Field(default=0.0)
    balance_after: float = Field(default=0.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
