from typing import Any
from uuid import UUID

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

    _user_id: UUID = Field(default_factory=UUID)  # 用户的唯一标识ID
    _currency: str = Field(default_factory=str)  # 货币种类
    _amount: float = Field(default_factory=float)  # 金额（+或-）
    _action_type: str = Field(default_factory=str)  # 操作类型（参考Method类）

    @property
    def user_id(self) -> UUID:
        """获取用户ID"""
        return self._user_id

    @property
    def currency(self) -> str:
        """获取货币种类"""
        return self._currency

    @currency.setter
    def currency(self, value: str):
        """设置货币种类"""
        self._currency = value

    @property
    def amount(self) -> float:
        """获取金额变化量"""
        return self._amount

    @amount.setter
    def amount(self, value: float):
        """设置金额变化量"""
        self._amount = value

    @property
    def action(self) -> str:
        """获取操作类型"""
        return self._action_type

    @action.setter
    def action(self, value: str):
        """设置操作类型"""
        self._action_type = value

    def cancel(self, msg: str = ""):
        """取消当前操作"""
        raise CancelAction(msg)


class TransactionComplete(BasicModel):
    """Transaction complete

    Args:
        BasicModel (BasicModel): extends pydantic BaseModel
    """

    _message: str = Field(default="")
    _source_balance: float = Field(default_factory=float)
    _new_balance: float = Field(default_factory=float)
    _timestamp: float = Field(default_factory=float)
    _user_id: UUID = Field(default_factory=UUID)

    @property
    def message(self) -> str:
        return self._message

    @property
    def source_balance(self) -> float:
        return self._source_balance

    @property
    def new_balance(self) -> float:
        return self._new_balance

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def UUID(self) -> UUID:
        return self._user_id
