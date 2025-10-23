# 事件钩子上下文
from dataclasses import dataclass, field

from .exception import CancelAction, DataUpdate


@dataclass
class TransactionContext:
    """Transaction context

    Args:
        BaseModel : extends pydantic BaseModel
    """

    user_id: str = field(default_factory=str)  # 用户的唯一标识ID
    currency: str = field(default_factory=str)  # 货币种类
    amount: float = field(default_factory=float)  # 金额（+或-）
    action_type: str = field(default_factory=str)  # 操作类型（参考Method类）

    def cancel(self, reason: str = ""):
        raise CancelAction(reason)

    def commit_update(self):
        raise DataUpdate(amount=self.amount)

@dataclass
class TransactionComplete:
    """Transaction complete

    Args:
        BaseModel : extends pydantic BaseModel
    """

    message: str = field(default="")
    source_balance: float = field(default_factory=float)
    new_balance: float = field(default_factory=float)
    timestamp: float = field(default_factory=float)
    user_id: str = field(default_factory=str)
