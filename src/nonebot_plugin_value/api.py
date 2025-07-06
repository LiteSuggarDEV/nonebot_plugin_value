from uuid import UUID

from nonebot_plugin_orm import AsyncSession

from .models.currency import Method
from .repository import AccountRepository, TransactionRepository


async def del_balance(
    session: AsyncSession,
    user_id: UUID,
    currency_id: str,
    amount: float,
    source: str = ""
):
    """异步减少余额"""
    account_repo = AccountRepository(session)
    tx_repo = TransactionRepository(session)
    try:
        account = await account_repo.get_or_create_account(user_id, currency_id)
        balance_before = await account_repo.get_balance(account.id)
        if balance_before is None:
            return {"success": False, "message": "账户不存在"}
        balance_after = balance_before - amount
        await tx_repo.create_transaction(
            account.id,
            currency_id,
            amount,
            Method.transfer_out(),
            source,
            balance_before,
            balance_after,
        )
    except Exception as e:
        return {"success": False, "error": str(e)}
async def add_balance(
    session: AsyncSession,
    user_id: UUID,
    currency_id: str,
    amount: float,
    source: str = ""
):
    """异步增加余额"""
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
        return {"success": False, "error": str(e)}


async def transfer_funds(
    session: AsyncSession,
    from_user_id: UUID,
    to_user_id: UUID,
    currency_id: str,
    amount: float,
    source: str = "transfer",
):
    """异步转账操作"""
    # 初始化仓库
    account_repo = AccountRepository(session)
    tx_repo = TransactionRepository(session)

    # 获取发送方账户
    from_account = await account_repo.get_or_create_account(from_user_id, currency_id)

    # 获取接收方账户
    to_account = await account_repo.get_or_create_account(to_user_id, currency_id)

    # 记录原始余额
    from_balance_before = from_account.balance
    to_balance_before = to_account.balance

    try:
        # 扣减发送方余额
        from_balance_before, from_balance_after = await account_repo.update_balance(
            from_account.id, -amount
        )

        # 增加接收方余额
        to_balance_before, to_balance_after = await account_repo.update_balance(
            to_account.id, amount
        )

        # 记录发送方交易
        await tx_repo.create_transaction(
            account_id=from_account.id,
            currency_id=currency_id,
            amount=-amount,
            action="TRANSFER_OUT",
            source=source,
            balance_before=from_balance_before,
            balance_after=from_balance_after,
        )

        # 记录接收方交易
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
