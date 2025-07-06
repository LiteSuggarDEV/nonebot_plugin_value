from datetime import datetime
from uuid import UUID as _UUID
from uuid import uuid4

from nonebot_plugin_orm import Model
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PlatformUser(Model):
    """平台用户表"""

    __tablename__ = "platform_users"

    # UUID作为主键（由外部算法生成）
    id:Mapped[_UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # 平台类型（如QQ、微信等）
    platform:Mapped[str] = mapped_column(String(32), nullable=False)

    # 平台用户ID
    user_id:Mapped[str] = mapped_column(String(64), nullable=False)

    # 唯一约束：同一平台同一用户只应有一条记录
    __table_args__ = (
        UniqueConstraint("platform", "user_id", name="uq_platform_user"),
        Index("idx_platform_user", "platform", "user_id"),
    )

    # 关系定义
    accounts = relationship("UserAccount", back_populates="user")


class UserAccount(Model):
    """用户账户表"""

    __tablename__ = "user_accounts"

    # UUID作为主键（由外部算法生成）
    id:Mapped[_UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # 用户外键
    user_id:Mapped[_UUID] = mapped_column(
        UUID, ForeignKey("platform_users.id", ondelete="CASCADE"), nullable=False
    )

    # 货币外键
    currency_id:Mapped[str] = mapped_column(
        String(32), ForeignKey("currency_meta.id", ondelete="RESTRICT"), nullable=False
    )

    # 账户余额
    balance:Mapped[float] = mapped_column(Numeric(16, 4), default=0.0)

    # 最后更新时间
    last_updated:Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系定义
    user = relationship("PlatformUser", back_populates="accounts")
    currency = relationship("CurrencyMeta", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")

    # 唯一约束：每个用户每种货币只能有一个账户
    __table_args__ = (
        UniqueConstraint("user_id", "currency_id", name="uq_user_currency"),
        Index("idx_user_currency", "user_id", "currency_id"),
    )


class Transaction(Model):
    """交易记录表"""

    __tablename__ = "transactions"

    # UUID作为主键
    id:Mapped[_UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # 账户外键
    account_id:Mapped[_UUID] = mapped_column(
        UUID, ForeignKey("user_accounts.id", ondelete="RESTRICT"), nullable=False
    )

    # 货币外键
    currency_id:Mapped[str] = mapped_column(
        String(32), ForeignKey("currency_meta.id", ondelete="RESTRICT"), nullable=False
    )

    # 交易金额
    amount:Mapped[float] = mapped_column(Numeric(16, 4), nullable=False)

    # 交易类型
    action: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # DEPOSIT, WITHDRAW, TRANSFER_IN, TRANSFER_OUT

    # 交易来源
    source:Mapped[str] = mapped_column(String(64), nullable=False)  # 发起交易的插件

    # 交易前后余额
    balance_before:Mapped[float] = mapped_column(Numeric(16, 4))
    balance_after:Mapped[float] = mapped_column(Numeric(16, 4))

    # 交易时间
    timestamp:Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系定义
    account = relationship("UserAccount", back_populates="transactions")
    currency = relationship("CurrencyMeta", back_populates="transactions")

    # 索引优化
    __table_args__ = (
        Index("idx_transaction_account", "account_id"),
        Index("idx_transaction_timestamp", "timestamp"),
    )


