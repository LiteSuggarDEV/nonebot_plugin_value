from datetime import datetime
from typing import Any

from nonebot import logger
from nonebot_plugin_orm import AsyncSession, get_session

from nonebot_plugin_value.models.balance import UserAccount

from ..action_type import Method
from ..db_api.currency import DEFAULT_CURRENCY_UUID
from ..hook.context import TransactionComplete, TransactionContext
from ..hook.exception import CancelAction
from ..hook.hooks_manager import HooksManager
from ..hook.hooks_type import HooksType
from ..repository import AccountRepository, TransactionRepository


async def del_account(
    account_id: str, session: AsyncSession | None = None, fail_then_throw: bool = False
) -> bool:
    """删除账户

    Args:
        session (AsyncSession | None, optional): 异步会话. Defaults to None.
        user_id (str): 用户ID
    """
    if session is None:
        session = get_session()
    async with session:
        try:
            await AccountRepository(session).remove_account(account_id)
            return True
        except Exception:
            if fail_then_throw:
                raise
            return False


async def list_accounts(
    session: AsyncSession,
    currency_id: str | None = None,
):
    """列出所有账户

    Args:
        session (AsyncSession): 异步会话. Defaults to None.

    Returns:
        Sequence[UserAccount]: 所有账户（指定或所有货币的）
    """
    if currency_id is None:
        currency_id = DEFAULT_CURRENCY_UUID.hex
    async with session:
        return await AccountRepository(session).list_accounts()


async def get_or_create_account(
    user_id: str,
    currency_id: str,
    session: AsyncSession,
) -> UserAccount:
    """获取或创建一个货币的账户

    Args:
        user_id (str): 用户ID
        currency_id (str): 货币ID
        session (AsyncSession): 异步会话. Defaults to None.

    Returns:
        UserAccount: 用户数据模型
    """
    async with session:
        return await AccountRepository(session).get_or_create_account(
            user_id, currency_id
        )


async def del_balance(
    user_id: str,
    currency_id: str,
    amount: float,
    source: str = "",
    session: AsyncSession | None = None,
) -> dict[str, Any]:
    """异步减少余额

    Args:
        user_id (str): 用户ID
        currency_id (str): 货币ID
        amount (float): 数量
        source (str, optional): 来源说明. Defaults to "".
        session (AsyncSession | None, optional): 数据库异步会话. Defaults to None.

    Returns:
        dict[str, Any]: 包含是否成功的说明
    """
    if not amount < 0:
        return {"success": False, "message": "减少金额不能大于0"}
    if session is None:
        session = get_session()
    async with session:
        account_repo = AccountRepository(session)
        tx_repo = TransactionRepository(session)
        has_commit: bool = False
        try:
            account = await account_repo.get_or_create_account(user_id, currency_id)
            session.add(account)
            balance_before = account.balance
            if balance_before is None:
                return {"success": False, "message": "账户不存在"}
            balance_after = balance_before - amount
            try:
                await HooksManager().run_hooks(
                    HooksType.pre(),
                    TransactionContext(
                        user_id=user_id,
                        currency=currency_id,
                        amount=amount,
                        action_type=Method.withdraw(),
                    ),
                )
            except CancelAction as e:
                logger.warning(f"取消了交易：{e.message}")
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
                        message="交易完成",
                        source_balance=balance_before,
                        new_balance=balance_after,
                        timestamp=datetime.now().timestamp(),
                        user_id=user_id,
                    ),
                )
            finally:
                return {"success": True, "message": "金额减少成功"}
        except Exception as e:
            if has_commit:
                await session.rollback()
            return {"success": False, "message": str(e)}


async def add_balance(
    user_id: str,
    currency_id: str,
    amount: float,
    source: str = "",
    session: AsyncSession | None = None,
) -> dict[str, Any]:
    """异步增加余额

    Args:
        user_id (str): 用户ID
        currency_id (str): 货币ID
        amount (float): 数量
        source (str, optional): 来源说明. Defaults to "".
        session (AsyncSession | None, optional): 数据库异步会话. Defaults to None.

    Returns:
        dict[str, Any]: 是否成功("success")，消息说明("message")
    """
    if session is None:
        session = get_session()
    async with session:
        if not amount > 0:
            return {"success": False, "message": "金额必须大于0"}
        account_repo = AccountRepository(session)
        tx_repo = TransactionRepository(session)
        has_commit: bool = False
        try:
            account = await account_repo.get_or_create_account(user_id, currency_id)
            session.add(account)
            balance_before = account.balance
            if balance_before is None:
                raise ValueError("账户不存在")
            try:
                await HooksManager().run_hooks(
                    HooksType.pre(),
                    TransactionContext(
                        user_id=user_id,
                        currency=currency_id,
                        amount=amount,
                        action_type=Method.deposit(),
                    ),
                )
            except CancelAction as e:
                logger.warning(f"取消了交易：{e.message}")
                return {"success": True, "message": f"取消了交易：{e.message}"}
            has_commit = True
            balance_after = account.balance + amount
            await tx_repo.create_transaction(
                account.id,
                currency_id,
                amount,
                Method.deposit(),
                source,
                account.balance,
                balance_after,
            )
            await account_repo.update_balance(account.id, balance_after)

            await session.commit()
            try:
                await HooksManager().run_hooks(
                    HooksType.post(),
                    TransactionComplete(
                        message="交易完成",
                        source_balance=balance_before,
                        new_balance=balance_after,
                        timestamp=datetime.now().timestamp(),
                        user_id=user_id,
                    ),
                )
            finally:
                return {"success": True, "message": "操作成功"}

        except Exception as e:
            if has_commit:
                await session.rollback()
            return {"success": False, "message": str(e)}


async def transfer_funds(
    fromuser_id: str,
    touser_id: str,
    currency_id: str,
    amount: float,
    source: str = "transfer",
    session: AsyncSession | None = None,
) -> dict[str, Any]:
    """异步转账

    Args:
        fromuser_id (str): 源用户ID
        touser_id (str): 目标用户ID
        currency_id (str): 货币ID
        amount (float): 数量
        source (str, optional): 源说明. Defaults to "transfer".
        session (AsyncSession | None, optional): 数据库异步Session. Defaults to None.

    Returns:
        dict[str, Any]: 如果成功则包含"from_balance"（源账户现在的balance），"to_balance"（目标账户现在的balance），否则包含"message"（错误消息）字段
    """
    if session is None:
        session = get_session()
    async with session:
        account_repo = AccountRepository(session)
        tx_repo = TransactionRepository(session)

        from_account = await account_repo.get_or_create_account(
            fromuser_id, currency_id
        )
        session.add(from_account)
        to_account = await account_repo.get_or_create_account(touser_id, currency_id)
        session.add(to_account)

        from_balance_before = from_account.balance
        to_balance_before = to_account.balance

        try:
            if amount<=0:
                raise ValueError("转账值为非负数！")
            try:
                await HooksManager().run_hooks(
                    HooksType.pre(),
                    TransactionContext(
                        user_id=fromuser_id,
                        currency=currency_id,
                        amount=amount,
                        action_type=Method.transfer_out(),
                    ),
                )
                await HooksManager().run_hooks(
                    HooksType.pre(),
                    TransactionContext(
                        user_id=touser_id,
                        currency=currency_id,
                        amount=amount,
                        action_type=Method.transfer_in(),
                    ),
                )
            except CancelAction as e:
                logger.info(f"取消了交易：{e.message}")
                return {"success": True, "message": f"取消了交易：{e.message}"}
            from_balance_before, from_balance_after = await account_repo.update_balance(
                from_account.id, -amount
            )
            to_balance_before, to_balance_after = await account_repo.update_balance(
                to_account.id, amount
            )
            timestamp = datetime.utcnow()
            await tx_repo.create_transaction(
                account_id=from_account.id,
                currency_id=currency_id,
                amount=-amount,
                action="TRANSFER_OUT",
                source=source,
                balance_before=from_balance_before,
                balance_after=from_balance_after,
                timestamp=timestamp,
            )
            await tx_repo.create_transaction(
                account_id=to_account.id,
                currency_id=currency_id,
                amount=amount,
                action="TRANSFER_IN",
                source=source,
                balance_before=to_balance_before,
                balance_after=to_balance_after,
                timestamp=timestamp,
            )

            # 提交事务
            await session.commit()
            try:
                await HooksManager().run_hooks(
                    HooksType.post(),
                    TransactionComplete(
                        message="交易完成(转账)",
                        source_balance=from_balance_before,
                        new_balance=from_balance_after,
                        timestamp=datetime.now().timestamp(),
                        user_id=fromuser_id,
                    ),
                )
                await HooksManager().run_hooks(
                    HooksType.post(),
                    TransactionComplete(
                        message="交易完成(转账)",
                        source_balance=to_balance_before,
                        new_balance=to_balance_after,
                        timestamp=datetime.now().timestamp(),
                        user_id=touser_id,
                    ),
                )
            finally:
                return {
                    "success": True,
                    "from_balance": from_balance_after,
                    "to_balance": to_balance_after,
                }

        except Exception as e:
            # 回滚事务
            await session.rollback()
            return {"success": False, "error": str(e)}
