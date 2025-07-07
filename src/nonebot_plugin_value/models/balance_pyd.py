from datetime import datetime

from pydantic import Field

from .base_pyd import BaseData


class PlatformUserData(BaseData):
    id: str = Field(default="")
    platform: str = Field(default="")
    user_id: str = Field(default="")


class UserAccountData(BaseData):
    id: str = Field(default="")
    user_id: str = Field(default="")
    currency_id: str = Field(default="")
    balance: float = Field(default=0.0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class TransactionData(BaseData):
    id: str = Field(default="")
    account_id: str = Field(default="")
    currency_id: str = Field(default="")
    amount: float = Field(default=0.0)
    action: str = Field(default="")
    source: str = Field(default="")
    balance_before: float = Field(default=0.0)
    balance_after: float = Field(default=0.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
