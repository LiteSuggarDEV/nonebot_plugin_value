from collections.abc import Sequence
from datetime import datetime, timezone

from nonebot_plugin_orm import AsyncSession
from sqlalchemy import delete, select

from ..exception import (
    AccountFrozen,
    AccountNotFound,
    CurrencyNotFound,
    TransactionException,
)
from ..models.balance import UserAccount
from ..models.currency import CurrencyMeta
from ..uuid_lib import get_uni_id


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
