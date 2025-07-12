# Repository,更加底层的数据库操作接口
from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import uuid1, uuid5

from nonebot_plugin_orm import AsyncSession
from sqlalchemy import insert, select, update

from .models.balance import Transaction, UserAccount
from .models.currency import CurrencyMeta
from .pyd_models.currency_pyd import CurrencyData
from .uuid_lib import NAMESPACE_VALUE

DEFAULT_NAME = "DEFAULT_CURRENCY_USD"
DEFAULT_CURRENCY_UUID = uuid5(NAMESPACE_VALUE, DEFAULT_NAME)


class CurrencyRepository:
    """货币元数据操作"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def createcurrency(self, currency_data: CurrencyData) -> CurrencyMeta:
        async with self.session as session:
            """创建新货币"""
            stmt = insert(CurrencyMeta).values(**dict(currency_data))
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

    async def update_currency(self, currency_data: CurrencyData) -> CurrencyMeta:
        """更新货币信息"""
        async with self.session as session:
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

    async def getcurrency(self, currency_id: str) -> CurrencyMeta | None:
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
            ).scalar_one_or_none()
            if not currency:
                raise ValueError("Currency not found")
            await session.delete(currency)
            users = await session.execute(
                select(UserAccount)
                .where(UserAccount.currency_id == currency_id)
                .with_for_update()
            )
            for user in users:
                await session.delete(user)
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
            # 获取货币配置
            stmt = (
                select(CurrencyMeta)
                .where(CurrencyMeta.id == currency_id)
                .with_for_update()
            )
            result = await session.execute(stmt)
            currency = result.scalar_one_or_none()
            if currency is None:
                raise ValueError(f"Currency {currency_id} not found")

            # 检查账户是否存在
            stmt = (
                select(UserAccount)
                .where(
                    UserAccount.id == user_id,
                    UserAccount.currency_id == currency_id,
                )
                .with_for_update()
            )
            result = await session.execute(stmt)
            account = result.scalar_one_or_none()

            if account is not None:
                session.add(account)
                return account

            session.add(currency)
            account = UserAccount(
                uni_id=uuid5(NAMESPACE_VALUE, f"{user_id}{currency_id}").hex,
                id=user_id,
                currency_id=currency_id,
                balance=currency.default_balance,
                last_updated=datetime.now(timezone.utc),
            )
            session.add(account)
            await session.commit()

            stmt = (
                select(UserAccount)
                .where(
                    UserAccount.id == user_id,
                    UserAccount.currency_id == currency_id,
                )
                .with_for_update()
            )
            result = await session.execute(stmt)
            account = result.scalar_one()
            session.add(account)
            return account

    async def get_balance(self, account_id: str) -> float | None:
        """获取账户余额"""
        account = await self.session.get(UserAccount, account_id)
        return account.balance if account else None

    async def update_balance(
        self, account_id: str, amount: float, currency_id: str
    ) -> tuple[float, float]:
        async with self.session as session:
            """更新余额"""

            # 获取账户
            account = (
                await session.execute(
                    select(UserAccount)
                    .where(
                        UserAccount.id == account_id,
                        UserAccount.currency_id == currency_id,
                    )
                    .with_for_update()
                )
            ).scalar_one_or_none()

            if account is None:
                raise ValueError("Account not found")
            session.add(account)

            # 获取货币规则
            currency = await session.get(CurrencyMeta, account.currency_id)
            session.add(currency)

            # 负余额检查
            if amount < 0 and not getattr(currency, "allow_negative", False):
                raise ValueError("Insufficient funds")

            # 记录原始余额
            old_balance = account.balance

            # 更新余额
            account.balance = amount
            await session.commit()

            return old_balance, amount

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

    async def remove_account(self, account_id: str):
        """删除账户"""
        async with self.session as session:
            stmt = (
                select(UserAccount)
                .where(UserAccount.id == account_id)
                .with_for_update()
            )
            accounts = (await session.execute(stmt)).scalars().all()
            if not accounts:
                raise ValueError("Account not found")
            for account in accounts:
                await session.delete(account)
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
            stmt = insert(Transaction).values(
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
            await session.execute(stmt)
            await session.commit()
            stmt = (
                select(Transaction)
                .where(
                    Transaction.id == uuid,
                    Transaction.timestamp == timestamp,
                )
                .with_for_update()
            )
            result = await session.execute(stmt)
            transaction = result.scalars().one()
            session.add(transaction)
            return transaction

    async def get_transaction_history(self, account_id: str, limit: int = 100):
        """获取账户交易历史"""
        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.account_id == account_id)
            .order_by(Transaction.timestamp.desc())
            .limit(limit)
            .with_for_update()
        )
        data = result.scalars().all()
        self.session.add_all(data)
        return data

    async def remove_transaction(self, transaction_id: str):
        """删除交易记录"""
        async with self.session as session:
            transaction = (
                await session.execute(
                    select(Transaction)
                    .where(Transaction.id == transaction_id)
                    .with_for_update()
                )
            ).scalar_one_or_none()
            if not transaction:
                raise ValueError("Transaction not found")
            await session.delete(transaction)
            await session.commit()
