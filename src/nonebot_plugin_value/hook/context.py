# 事件钩子上下文
from typing import Any

from pydantic import BaseModel, Field

from .exception import CancelAction


class BasicModel(BaseModel):
    """Base context for all hooks

    Args:
        BaseModel (BaseModel): extends pydantic BaseModel
    """

    def __getitem__(self, key: str) -> Any:
        if not hasattr(self, key):
            raise KeyError(f"Key {key} not found in context")
        return getattr(self, key)


class TransactionContext(BasicModel):
    """Transaction context

    Args:
        BasicModel (BasicModel): extends pydantic BaseModel
    """

    user_id: str = Field(default_factory=str)  # 用户的唯一标识ID
    currency: str = Field(default_factory=str)  # 货币种类
    amount: float = Field(default_factory=float)  # 金额（+或-）
    action_type: str = Field(default_factory=str)  # 操作类型（参考Method类）

    def cancel(self, reason: str = ""):
        raise CancelAction(reason)


class TransactionComplete(BasicModel):
    """Transaction complete

    Args:
        BasicModel (BasicModel): extends pydantic BaseModel
    """

    message: str = Field(default="")
    source_balance: float = Field(default_factory=float)
    new_balance: float = Field(default_factory=float)
    timestamp: float = Field(default_factory=float)
    user_id: str = Field(default_factory=str)
