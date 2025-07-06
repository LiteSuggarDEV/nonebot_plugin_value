from datetime import datetime
from uuid import UUID

from nonebot_plugin_orm import AsyncSession

from .action_type import Method
from .hook.context import TransactionComplete, TransactionContext
from .hook.exception import CancelAction
from .hook.hooks_manager import HooksManager
from .hook.hooks_type import HooksType
from .repository import AccountRepository, TransactionRepository


async def del_balance(
    session: AsyncSession,
    user_id: UUID,
    currency_id: str,
    amount: float,
    source: str = "",
):
    """异步减少余额"""
    if not amount < 0:
        return {"success": False, "message": "减少金额不能大于0"}
    account_repo = AccountRepository(session)
    tx_repo = TransactionRepository(session)
    has_commit: bool = False
    try:
        account = await account_repo.get_or_create_account(user_id, currency_id)
        balance_before = await account_repo.get_balance(account.id)
        if balance_before is None:
            return {"success": False, "message": "账户不存在"}
        balance_after = balance_before - amount
        try:
            await HooksManager().run_hooks(
                HooksType.pre(),
                TransactionContext(
                    _user_id=user_id,
                    _currency=currency_id,
                    _amount=amount,
                    _action_type=Method.withdraw(),
                ),
            )
        except CancelAction as e:
            return {"success": True, "message": f"取消了交易：{e.message}"}
        has_commit = True
        await account_repo.update_balance(account.id, balance_after)
        await tx_repo.create_transaction(
            account.id,
            currency_id,
            amount,
            Method.transfer_out(),
            source,
            balance_before,
            balance_after,
        )
        try:
            await HooksManager().run_hooks(
                HooksType.post(),
                TransactionComplete(
                    _message="交易完成",
                    _source_balance=balance_before,
                    _new_balance=balance_after,
                    _timestamp=datetime.now().timestamp(),
                    _user_id=user_id,
                ),
            )
        finally:
            return {"success": True, "message": "金额减少成功"}
    except Exception as e:
        if has_commit:
            await session.rollback()
        return {"success": False, "message": str(e)}


async def add_balance(
    session: AsyncSession,
    user_id: UUID,
    currency_id: str,
    amount: float,
    source: str = "",
):
    """异步增加余额"""
    if not amount > 0:
        return {"success": False, "message": "金额必须大于0"}
    account_repo = AccountRepository(session)
    tx_repo = TransactionRepository(session)
    has_commit: bool = False
    try:
        account = await account_repo.get_or_create_account(user_id, currency_id)
        balance_before = await account_repo.get_balance(account.id)
        if balance_before is None:
            raise ValueError("账户不存在")
        has_commit = True
        await tx_repo.create_transaction(
            account.id,
            currency_id,
            amount,
            Method.deposit(),
            source,
            account.balance,
            account.balance + amount,
        )
        await account_repo.update_balance(account.id, account.balance + amount)

        await session.commit()
        return {"success": True, "message": "操作成功"}
    except Exception as e:
        if has_commit:
            await session.rollback()
        return {"success": False, "message": str(e)}


async def transfer_funds(
    session: AsyncSession,
    from_user_id: UUID,
    to_user_id: UUID,
    currency_id: str,
    amount: float,
    source: str = "transfer",
):
    """异步转账操作"""
    account_repo = AccountRepository(session)
    tx_repo = TransactionRepository(session)

    from_account = await account_repo.get_or_create_account(from_user_id, currency_id)
    to_account = await account_repo.get_or_create_account(to_user_id, currency_id)

    from_balance_before = from_account.balance
    to_balance_before = to_account.balance

    try:
        from_balance_before, from_balance_after = await account_repo.update_balance(
            from_account.id, -amount
        )
        to_balance_before, to_balance_after = await account_repo.update_balance(
            to_account.id, amount
        )

        await tx_repo.create_transaction(
            account_id=from_account.id,
            currency_id=currency_id,
            amount=-amount,
            action="TRANSFER_OUT",
            source=source,
            balance_before=from_balance_before,
            balance_after=from_balance_after,
        )
        await tx_repo.create_transaction(
            account_id=to_account.id,
            currency_id=currency_id,
            amount=amount,
            action="TRANSFER_IN",
            source=source,
            balance_before=to_balance_before,
            balance_after=to_balance_after,
        )

        # 提交事务
        await session.commit()

        return {
            "success": True,
            "from_balance": from_balance_after,
            "to_balance": to_balance_after,
        }

    except Exception as e:
        # 回滚事务
        await session.rollback()
        return {"success": False, "error": str(e)}
