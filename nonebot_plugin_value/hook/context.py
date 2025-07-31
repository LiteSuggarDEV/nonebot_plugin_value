# 事件钩子上下文
from pydantic import BaseModel, Field

from .exception import CancelAction, DataUpdate


class TransactionContext(BaseModel):
    """Transaction context

    Args:
        BaseModel (BaseModel): extends pydantic BaseModel
    """

    user_id: str = Field(default_factory=str)  # 用户的唯一标识ID
    currency: str = Field(default_factory=str)  # 货币种类
    amount: float = Field(default_factory=float)  # 金额（+或-）
    action_type: str = Field(default_factory=str)  # 操作类型（参考Method类）

    def cancel(self, reason: str = ""):
        raise CancelAction(reason)

    def commit_update(self):
        raise DataUpdate(amount=self.amount)


class TransactionComplete(BaseModel):
    """Transaction complete

    Args:
        BaseModel (BaseModel): extends pydantic BaseModel
    """

    message: str = Field(default="")
    source_balance: float = Field(default_factory=float)
    new_balance: float = Field(default_factory=float)
    timestamp: float = Field(default_factory=float)
    user_id: str = Field(default_factory=str)
