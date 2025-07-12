from typing import Any

from pydantic import BaseModel, Field


class ActionResult(BaseModel):
    """操作结果基类"""

    success: bool = Field(default_factory=bool)
    message: str = Field(default_factory=str)

    def __getitem__(self, key: str):
        if key not in self.model_dump():
            raise KeyError(key)
        return getattr(self, key)

    def __setitem__(self, key: str, value: str):
        if key not in self.model_dump():
            raise KeyError(key)
        setattr(self, key, value)

    def get(self, key: str, default: Any | None = None):
        return getattr(self, key, default)


class TransferResult(ActionResult):
    """转账结果"""

    from_balance: float | None = Field(default=None)
    to_balance: float | None = Field(default=None)
