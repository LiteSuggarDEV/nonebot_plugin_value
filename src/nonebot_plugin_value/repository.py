from nonebot_plugin_orm import AsyncSession
from sqlalchemy import select

from .models.balance import Transaction, UserAccount
from .models.currency import CurrencyMeta
from .models.currency_pyd import CurrencyData


class CurrencyRepository:
    """货币元数据操作"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def createcurrency(self, currency_data: CurrencyData) -> CurrencyMeta:
        """创建新货币"""
        currency = CurrencyMeta(**dict(currency_data))
        self.session.add(currency)
        await self.session.flush()
        return currency

    async def getcurrency(self, currency_id: str) -> CurrencyMeta | None:
        """获取货币信息"""
        result = await self.session.execute(
            select(CurrencyMeta).where(CurrencyMeta.id == currency_id)
        )
        return result.scalar_one_or_none()

    async def list_currencies(self):
        """列出所有货币"""
        result = await self.session.execute(select(CurrencyMeta))
        return result.scalars().all()


class AccountRepository:
    """账户操作"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_account(
        self, user_id: str, currency_id: str
    ) -> UserAccount:
        """获取或创建用户账户"""
        # 检查账户是否存在
        account = await self.session.execute(
            select(UserAccount)
            .where(UserAccount.user_id == user_id)
            .where(UserAccount.currency_id == currency_id)
            .with_for_update()  # 行级锁
        )
        account = account.scalar_one_or_none()

        if account:
            return account

        # 获取货币配置
        currency = await self.session.get(CurrencyMeta, currency_id)
        if not currency:
            raise ValueError(f"Currency {currency_id} not found")

        # 创建新账户
        new_account = UserAccount(
            user_id=user_id, currency_id=currency_id, balance=currency.default_balance
        )
        self.session.add(new_account)
        await self.session.flush()
        return new_account

    async def get_balance(self, account_id: str) -> float | None:
        """获取账户余额"""
        account = await self.session.get(UserAccount, account_id)
        return account.balance if account else None

    async def update_balance(
        self, account_id: str, delta: float
    ) -> tuple[float, float]:
        """原子更新余额"""
        # 获取账户（带锁）
        account = await self.session.get(UserAccount, account_id)

        if not account:
            raise ValueError("Account not found")

        # 获取货币规则
        currency = await self.session.get(CurrencyMeta, account.currency_id)

        # 计算新余额
        new_balance = account.balance + delta

        # 负余额检查
        if new_balance < 0 and not getattr(currency, "allow_negative", False):
            raise ValueError("Insufficient funds")

        # 记录原始余额
        old_balance = account.balance

        # 更新余额
        account.balance = new_balance
        await self.session.flush()

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
    ) -> Transaction:
        """创建交易记录"""
        transaction = Transaction(
            account_id=account_id,
            currency_id=currency_id,
            amount=amount,
            action=action,
            source=source,
            balance_before=balance_before,
            balance_after=balance_after,
        )
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    async def get_transaction_history(self, account_id: str, limit: int = 100):
        """获取账户交易历史"""
        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.account_id == account_id)
            .order_by(Transaction.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
