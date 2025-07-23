from typing import Any

from pydantic import BaseModel, Field


class ActionResult(BaseModel):
    """操作结果基类"""

    success: bool = Field(default_factory=bool)
    message: str = Field(default_factory=str)

    def get(self, key: str, default: Any | None = None):
        return getattr(self, key, default)


class TransferResult(ActionResult):
    """转账结果"""

    from_balance: float | None = Field(default=None)
    to_balance: float | None = Field(default=None)
