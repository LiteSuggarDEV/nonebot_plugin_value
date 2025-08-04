from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import uuid1

from nonebot_plugin_orm import AsyncSession
from sqlalchemy import delete, select

from ..exception import (
    TransactionNotFound,
)
from ..models.balance import Transaction


class TransactionRepository:
    """交易操作"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transaction(
        self,
        account_id: str,
        currency_id: str,
        amount: float,
        action: str,
        source: str,
        balance_before: float,
        balance_after: float,
        timestamp: datetime | None = None,
    ) -> Transaction:
        async with self.session as session:
            """创建交易记录"""
            if timestamp is None:
                timestamp = datetime.now(timezone.utc)
            uuid = uuid1().hex
            transaction_data = Transaction(
                id=uuid,
                account_id=account_id,
                currency_id=currency_id,
                amount=amount,
                action=action,
                source=source,
                balance_before=balance_before,
                balance_after=balance_after,
                timestamp=timestamp,
            )
            session.add(transaction_data)
            await session.commit()
            await session.refresh(transaction_data)
            session.add(transaction_data)
            return transaction_data

    async def get_transaction_history(
        self, account_id: str, limit: int = 100
    ) -> Sequence[Transaction]:
        """获取账户交易历史"""
        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.account_id == account_id)
            .order_by(Transaction.timestamp.desc())
            .limit(limit)
        )
        data = result.scalars().all()
        self.session.add_all(data)
        return data

    async def get_transaction_history_by_time_range(
        self,
        account_id: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 100,
    ) -> Sequence[Transaction]:
        """获取账户交易历史"""
        async with self.session as session:
            result = await session.execute(
                select(Transaction)
                .where(
                    Transaction.account_id == account_id,
                    Transaction.timestamp >= start_time,
                    Transaction.timestamp <= end_time,
                )
                .order_by(Transaction.timestamp.desc())
                .limit(limit)
            )
            data = result.scalars().all()
            session.add_all(data)
        return data

    async def remove_transaction(self, transaction_id: str) -> None:
        """删除交易记录"""
        async with self.session as session:
            try:
                transaction = (
                    await session.execute(
                        select(Transaction)
                        .where(Transaction.id == transaction_id)
                        .with_for_update()
                    )
                ).scalar()
                if not transaction:
                    raise TransactionNotFound("Transaction not found")
                stmt = delete(Transaction).where(Transaction.id == transaction_id)
                await session.execute(stmt)
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()
