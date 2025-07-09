from datetime import datetime

from pydantic import Field

from .base_pyd import BaseData


class UserAccountData(BaseData):
    uni_id: str = Field(default="")
    id: str = Field(default="")
    currency_id: str = Field(default="")
    balance: float = Field(default=0.0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


