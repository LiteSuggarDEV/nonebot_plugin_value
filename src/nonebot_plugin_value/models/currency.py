from datetime import datetime
from uuid import uuid4

from nonebot_plugin_orm import Model
from sqlalchemy import Boolean, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CurrencyMeta(Model):
    """货币元数据表"""

    __tablename__ = "currency_meta"

    # 货币ID作为主键
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=uuid4)

    # 货币显示名称
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)

    # 货币符号
    symbol: Mapped[str] = mapped_column(String(5), default="$")

    # 默认余额
    default_balance: Mapped[float] = mapped_column(Numeric(16, 4), default=0.0)

    # 是否允许负余额
    allow_negative: Mapped[bool] = mapped_column(Boolean, default=False)

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系定义
    accounts = relationship("UserAccount", back_populates="currency")
    transactions = relationship("Transaction", back_populates="currency")
