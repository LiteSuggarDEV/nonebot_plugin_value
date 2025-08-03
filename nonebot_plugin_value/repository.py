# Repository,更加底层的数据库操作接口
from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import uuid1

from nonebot import logger
from nonebot_plugin_orm import AsyncSession
from sqlalchemy import delete, select, update

from .exception import (
    AccountFrozen,
    AccountNotFound,
    CurrencyNotFound,
    TransactionException,
    TransactionNotFound,
)
from .models.balance import Transaction, UserAccount
from .models.currency import CurrencyMeta
from .pyd_models.currency_pyd import CurrencyData
from .uuid_lib import DEFAULT_CURRENCY_UUID, DEFAULT_NAME, NAMESPACE_VALUE, get_uni_id

__all__ = [
    "DEFAULT_CURRENCY_UUID",
    "DEFAULT_NAME",
    "NAMESPACE_VALUE",
]


class CurrencyRepository:
    """货币元数据操作"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_currency(
        self, currency_data: CurrencyData
    ) -> tuple[CurrencyMeta, bool]:
        """获取或创建货币"""
        async with self.session as session:
            stmt = await session.execute(
                select(CurrencyMeta).where(
                    CurrencyMeta.id == currency_data.id,
                )
            )
            if (currency := stmt.scalars().first()) is not None:
                session.add(currency)
                return currency, True
            result = await self.createcurrency(currency_data)
            return result, False

    async def createcurrency(self, currency_data: CurrencyData) -> CurrencyMeta:
        async with self.session as session:
            """创建新货币"""
            currency = CurrencyMeta(**currency_data.model_dump())
            session.add(currency)
            await session.commit()
            await session.refresh(currency)
            return currency

    async def update_currency(self, currency_data: CurrencyData) -> CurrencyMeta:
        """更新货币信息"""
        async with self.session as session:
            try:
                stmt = (
                    update(CurrencyMeta)
                    .where(CurrencyMeta.id == currency_data.id)
                    .values(**dict(currency_data))
                )
                await session.execute(stmt)
                await session.commit()
                stmt = (
                    select(CurrencyMeta)
                    .where(CurrencyMeta.id == currency_data.id)
                    .with_for_update()
                )
                result = await session.execute(stmt)
                currency_meta = result.scalar_one()
                session.add(currency_meta)
                return currency_meta
            except Exception:
                await session.rollback()
                raise

    async def get_currency(self, currency_id: str) -> CurrencyMeta | None:
        """获取货币信息"""
        async with self.session as session:
            result = await self.session.execute(
                select(CurrencyMeta).where(CurrencyMeta.id == currency_id)
            )
            currency_meta = result.scalar_one_or_none()
            if currency_meta:
                session.add(currency_meta)
                return currency_meta
            return None

    async def list_currencies(self) -> Sequence[CurrencyMeta]:
        """列出所有货币"""
        async with self.session as session:
            result = await self.session.execute(select(CurrencyMeta))
            data = result.scalars().all()
            session.add_all(data)
            return data

    async def remove_currency(self, currency_id: str):
        """删除货币（警告！会同时删除所有关联账户！）"""
        async with self.session as session:
            currency = (
                await session.execute(
                    select(CurrencyMeta)
                    .where(CurrencyMeta.id == currency_id)
                    .with_for_update()
                )
            ).scalar()
            if currency is None:
                raise CurrencyNotFound(f"Currency {currency_id} not found")
            try:
                logger.warning(f"Deleting currency {currency_id}")
                stmt = delete(CurrencyMeta).where(CurrencyMeta.id == currency_id)
                await session.execute(stmt)
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()


class AccountRepository:
    """账户操作"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_account(
        self, user_id: str, currency_id: str
    ) -> UserAccount:
        async with self.session as session:
            """获取或创建用户账户"""
            try:
                # 获取货币配置
                stmt = select(CurrencyMeta).where(CurrencyMeta.id == currency_id)
                result = await session.execute(stmt)
                currency = result.scalar_one_or_none()
                if currency is None:
                    raise CurrencyNotFound(f"Currency {currency_id} not found")

                # 检查账户是否存在
                stmt = (
                    select(UserAccount)
                    .where(UserAccount.uni_id == get_uni_id(user_id, currency_id))
                    .with_for_update()
                )
                result = await session.execute(stmt)
                account = result.scalar_one_or_none()

                if account is not None:
                    session.add(account)
                    return account

                session.add(currency)
                account = UserAccount(
                    uni_id=get_uni_id(user_id, currency_id),
                    id=user_id,
                    currency_id=currency_id,
                    balance=currency.default_balance,
                    last_updated=datetime.now(timezone.utc),
                )
                session.add(account)
                await session.commit()
                await session.refresh(account)
                return account
            except Exception:
                await session.rollback()
                raise

    async def set_account_frozen(
        self,
        account_id: str,
        currency_id: str,
        frozen: bool,
    ) -> None:
        """设置账户冻结状态"""
        async with self.session as session:
            try:
                account = await self.get_or_create_account(account_id, currency_id)
                session.add(account)
                account.frozen = frozen
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()

    async def set_frozen_all(self, account_id: str, frozen: bool):
        async with self.session as session:
            try:
                result = await session.execute(
                    select(UserAccount).where(UserAccount.id == account_id)
                )
                accounts = result.scalars().all()
                session.add_all(accounts)
                for account in accounts:
                    account.frozen = frozen
            except Exception as e:
                await session.rollback()
                raise e
            else:
                await session.commit()

    async def is_account_frozen(
        self,
        account_id: str,
        currency_id: str,
    ) -> bool:
        """判断账户是否冻结"""
        async with self.session:
            return (await self.get_or_create_account(account_id, currency_id)).frozen

    async def get_balance(self, account_id: str, currency_id: str) -> float | None:
        """获取账户余额"""
        uni_id = get_uni_id(account_id, currency_id)
        account = await self.session.get(UserAccount, uni_id)
        return account.balance if account else None

    async def update_balance(
        self, account_id: str, amount: float, currency_id: str
    ) -> tuple[float, float]:
        async with self.session as session:
            """更新余额"""
            try:
                # 获取账户
                account = (
                    await session.execute(
                        select(UserAccount)
                        .where(
                            UserAccount.uni_id == get_uni_id(account_id, currency_id)
                        )
                        .with_for_update()
                    )
                ).scalar_one_or_none()

                if account is None:
                    raise AccountNotFound("Account not found")
                session.add(account)

                if account.frozen:
                    raise AccountFrozen(
                        f"Account {account_id} on currency {currency_id} is frozen"
                    )

                # 获取货币规则
                currency = await session.get(CurrencyMeta, account.currency_id)
                session.add(currency)

                # 负余额检查
                if amount < 0 and not getattr(currency, "allow_negative", False):
                    raise TransactionException("Insufficient funds")

                # 记录原始余额
                old_balance = account.balance

                # 更新余额
                account.balance = amount
                await session.commit()

                return old_balance, amount
            except Exception:
                await session.rollback()
                raise

    async def list_accounts(
        self, currency_id: str | None = None
    ) -> Sequence[UserAccount]:
        """列出所有账户"""
        async with self.session as session:
            if not currency_id:
                result = await session.execute(select(UserAccount).with_for_update())
            else:
                result = await session.execute(
                    select(UserAccount)
                    .where(UserAccount.currency_id == currency_id)
                    .with_for_update()
                )
            data = result.scalars().all()
            if len(data) > 0:
                session.add_all(data)
            return data

    async def remove_account(self, account_id: str, currency_id: str | None = None):
        """删除账户"""
        async with self.session as session:
            try:
                if not currency_id:
                    stmt = (
                        select(UserAccount)
                        .where(UserAccount.id == account_id)
                        .with_for_update()
                    )
                else:
                    stmt = (
                        select(UserAccount)
                        .where(
                            UserAccount.uni_id == get_uni_id(account_id, currency_id)
                        )
                        .with_for_update()
                    )
                accounts = (await session.execute(stmt)).scalars().all()
                if not accounts:
                    raise AccountNotFound("Account not found")
                for account in accounts:
                    stmt = delete(UserAccount).where(UserAccount.id == account.id)
                    await session.execute(stmt)
            except Exception:
                await session.rollback()
            else:
                await session.commit()


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
