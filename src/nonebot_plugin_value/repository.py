import uuid
from datetime import datetime
from uuid import uuid5

from nonebot_plugin_orm import AsyncSession
from sqlalchemy import insert, select

from .models.balance import Transaction, UserAccount
from .models.currency import CurrencyMeta
from .models.currency_pyd import CurrencyData

DEFAULT_NAME = "DEFAULT_CURRENCY_USD"
DEFAULT_CURRENCY_UUID = uuid5(uuid.NAMESPACE_X500, "nonebot_plugin_value")


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
            stmt = select(CurrencyMeta).where(CurrencyMeta.id == currency_data.id)
            result = await session.execute(stmt)
            currency_meta = result.scalar_one()
            session.add(currency_meta)
            return currency_meta

    async def getcurrency(self, currency_id: str) -> CurrencyMeta | None:
        """获取货币信息"""
        result = await self.session.execute(
            select(CurrencyMeta).where(CurrencyMeta.id == currency_id)
        )
        currency_meta = result.scalar_one_or_none()
        if currency_meta:
            self.session.add(currency_meta)
            return currency_meta
        return None

    async def list_currencies(self):
        """列出所有货币"""
        result = await self.session.execute(select(CurrencyMeta))
        data = result.scalars().all()
        self.session.add_all(data)
        return data


class AccountRepository:
    """账户操作"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_account(
        self, user_id: str, currency_id: str
    ) -> UserAccount:
        async with self.session as session:
            """获取或创建用户账户"""
            # 检查账户是否存在
            account = await session.execute(
                select(UserAccount)
                .where(UserAccount.user_id == user_id)
                .where(UserAccount.currency_id == currency_id)
                .with_for_update()  # 行级锁
            )
            account = account.scalar_one_or_none()

            if account:
                session.add(account)
                return account

            # 获取货币配置
            currency = await session.get(CurrencyMeta, currency_id)
            if not currency:
                raise ValueError(f"Currency {currency_id} not found")
            session.add(currency)
            stmt = insert(UserAccount).values(
                user_id=user_id,
                currency_id=currency_id,
                balance=currency.default_balance,
            )
            await session.execute(stmt)
            await session.commit()

            stmt = select(UserAccount).where(
                UserAccount.user_id == user_id, UserAccount.currency_id == currency_id
            )
            result = await session.execute(stmt)

            return result.scalar_one()

    async def get_balance(self, account_id: str) -> float | None:
        """获取账户余额"""
        account = await self.session.get(UserAccount, account_id)
        return account.balance if account else None

    async def update_balance(
        self, account_id: str, delta: float
    ) -> tuple[float, float]:
        async with self.session as session:
            """原子更新余额"""

            # 获取账户（带锁）
            account = await session.get(UserAccount, account_id)

            if not account:
                raise ValueError("Account not found")
            session.add(account)

            # 获取货币规则
            currency = await session.get(CurrencyMeta, account.currency_id)

            # 计算新余额
            new_balance = account.balance + delta

            # 负余额检查
            if new_balance < 0 and not getattr(currency, "allow_negative", False):
                raise ValueError("Insufficient funds")

            # 记录原始余额
            old_balance = account.balance

            # 更新余额
            account.balance = new_balance
            await session.commit()

            return old_balance, new_balance


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
                timestamp = datetime.utcnow()
            stmt = insert(Transaction).values(
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
            stmt = select(Transaction).where(
                Transaction.account_id == account_id,
                Transaction.currency_id == currency_id,
                Transaction.action == action,
                Transaction.source == source,
                Transaction.timestamp == timestamp,
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
        )
        data = result.scalars().all()
        self.session.add_all(data)
        return data
