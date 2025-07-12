from pydantic import Field

from .base_pyd import BaseData


class CurrencyData(BaseData):
    allow_negative: bool = Field(default=False)
    display_name: str = Field(default="Dollar")
    id: str = Field(default="")
    symbol: str = Field(default="$")
    default_balance: float = Field(default=0.0)
