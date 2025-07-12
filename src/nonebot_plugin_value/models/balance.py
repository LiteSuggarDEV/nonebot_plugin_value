import uuid
from datetime import datetime, timezone
from typing import Any

from nonebot_plugin_orm import Model
from sqlalchemy import (
    FLOAT,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import MappedColumn, mapped_column, relationship

from ..uuid_lib import NAMESPACE_VALUE


class UserAccount(Model):
    """用户账户表"""

    __tablename__ = "user_accounts"

    # 每种货币账户的唯一ID(id currency_id-UUID.hex)
    uni_id: MappedColumn[str] = mapped_column(String(64), primary_key=True)

    # 用户ID
    id: MappedColumn[str] = mapped_column(String(64))

    # 货币外键
    currency_id: MappedColumn[str] = mapped_column(
        String(64), ForeignKey("currency_meta.id", ondelete="CASCADE"), nullable=False
    )

    # 账户余额
    balance: MappedColumn[float] = mapped_column(FLOAT, default=0.0)

    # 最后更新时间
    last_updated: MappedColumn[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    currency = relationship("CurrencyMeta", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")

    # 唯一约束：每个用户每种货币只能有一个账户
    __table_args__ = (
        UniqueConstraint("id", "currency_id", name="uq_usercurrency"),
        Index("idx_usercurrency", "id", "currency_id"),
    )

    def __init__(self, **kwargs: Any):
        if "id" not in kwargs or "currency_id" not in kwargs:
            raise ValueError("id and currency_id must be provided")
        if "uni_id" not in kwargs:
            namespace = NAMESPACE_VALUE
            uni_id_val = uuid.uuid5(namespace, kwargs["id"] + kwargs["currency_id"])
            kwargs["id"] = uni_id_val
        super().__init__(**kwargs)


class Transaction(Model):
    """交易记录表"""

    __tablename__ = "transactions"

    # UUID作为主键
    id: MappedColumn[str] = mapped_column(String(64), primary_key=True)

    # 账户外键
    account_id: MappedColumn[str] = mapped_column(
        String, ForeignKey("user_accounts.id", ondelete="RESTRICT"), nullable=False
    )

    # 货币外键
    currency_id: MappedColumn[str] = mapped_column(
        String(32), ForeignKey("currency_meta.id", ondelete="RESTRICT"), nullable=False
    )

    # 交易金额
    amount: MappedColumn[float] = mapped_column(FLOAT, nullable=False)

    # 交易类型
    action: MappedColumn[str] = mapped_column(
        String(20), nullable=False
    )  # DEPOSIT, WITHDRAW, TRANSFER_IN, TRANSFER_OUT

    # 交易来源
    source: MappedColumn[str] = mapped_column(
        String(64), nullable=False
    )  # 发起交易的插件

    # 交易前后余额
    balance_before: MappedColumn[float] = mapped_column(FLOAT)
    balance_after: MappedColumn[float] = mapped_column(FLOAT)

    # 交易时间
    timestamp: MappedColumn[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
    )

    # 关系定义
    account = relationship("UserAccount", back_populates="transactions")
    currency = relationship("CurrencyMeta", back_populates="transactions")

    # 索引优化
    __table_args__ = (
        Index("idx_transaction_account", "account_id"),
        Index("idx_transactiontimestamp", "timestamp"),
    )
