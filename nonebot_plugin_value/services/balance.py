from datetime import datetime, timezone

from nonebot import logger
from nonebot_plugin_orm import AsyncSession, get_session

from ..action_type import Method
from ..hook.context import TransactionComplete, TransactionContext
from ..hook.exception import CancelAction, DataUpdate
from ..hook.hooks_manager import HooksManager
from ..hook.hooks_type import HooksType
from ..models.balance import UserAccount
from ..pyd_models.action import ActionResult, TransferResult
from ..repository import AccountRepository, TransactionRepository
from ..services.currency import DEFAULT_CURRENCY_UUID


async def set_frozen(
    account_id: str,
    frozen: bool,
    currency_id: str | None = None,
    session: AsyncSession | None = None,
) -> None:
    """设置账户特定货币的冻结状态

    Args:
        account_id (str): 账户ID
        frozen (bool): 是否冻结
        currency_id (str | None, optional): 货币ID. Defaults to None.
        session (AsyncSession | None, optional): 异步Session. Defaults to None.
    """
    if session is None:
        session = get_session()
    async with session:
        repo = AccountRepository(session)
        await repo.set_account_frozen(
            account_id, currency_id or DEFAULT_CURRENCY_UUID.hex, frozen
        )


async def set_frozen_all(
    account_id: str,
    frozen: bool,
    session: AsyncSession | None = None,
):
    """冻结这个账户ID下的所有货币储备

    Args:
        account_id (str): 账户ID
        frozen (bool): 是否冻结
        session (AsyncSession | None, optional): 异步Session. Defaults to None.
    """
    if session is None:
        session = get_session()
    async with session:
        await AccountRepository(session).set_frozen_all(account_id, frozen)


async def del_account(
    account_id: str,
    session: AsyncSession | None = None,
    fail_then_throw: bool = False,
    currency_id: str | None = None,
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
            await AccountRepository(session).remove_account(account_id, currency_id)
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


async def batch_del_balance(
    updates: list[tuple[str, float]],
    currency_id: str,
    source: str = "batch_update",
    session: AsyncSession | None = None,
    return_all_on_fail: bool = False,
) -> list[ActionResult]:
    """批量减少账户余额

    Args:
        updates (list[tuple[str, float]]): 元组列表，包含用户id和金额
        currency_id (str): 货币ID
        source (str, optional): 源. Defaults to "batch_update".
        session (AsyncSession | None, optional): 异步Session. Defaults to None.
        return_all_on_fail (bool, optional): 批量操作失败时是否仍然返回所有结果. Defaults to False.

    Returns:
        list[ActionResult]: 操作结果列表
    """
    if session is None:
        session = get_session()
    result_list: list[ActionResult] = []
    async with session:
        for uid, amount in updates:
            data: ActionResult = await del_balance(
                uid, currency_id, amount, source, session
            )
            result_list.append(data)

        if not all(r.success for r in result_list):
            return [] if not return_all_on_fail else result_list
        return result_list


async def del_balance(
    user_id: str,
    currency_id: str,
    amount: float,
    source: str = "",
    session: AsyncSession | None = None,
) -> ActionResult:
    """异步减少余额

    Args:
        user_id (str): 用户ID
        currency_id (str): 货币ID
        amount (float): 金额
        source (str, optional): 来源说明. Defaults to "".
        session (AsyncSession | None, optional): 数据库异步会话. Defaults to None.

    Returns:
        ActionResult: 包含是否成功的说明
    """
    if amount <= 0:
        return ActionResult(success=False, message="金额必须大于0")
    if session is None:
        session = get_session()
    async with session:
        account_repo = AccountRepository(session)
        tx_repo = TransactionRepository(session)

        account = await account_repo.get_or_create_account(user_id, currency_id)
        session.add(account)
        balance_before = account.balance
        account_id = account.id
        try:
            await HooksManager().run_hooks(
                HooksType.PRE.value,
                TransactionContext(
                    user_id=user_id,
                    currency=currency_id,
                    amount=amount,
                    action_type=Method.WITHDRAW.value,
                ),
            )
        except DataUpdate as du:
            amount = du.amount
        except CancelAction as e:
            logger.warning(f"取消了交易：{e.message}")
            return TransferResult(
                success=True,
                message=f"取消了交易：{e.message}",
            )
        balance_after = balance_before - amount
        await account_repo.update_balance(
            account_id,  # 使用提前获取的account_id
            balance_after,
            currency_id,
        )
        await tx_repo.create_transaction(
            account_id,  # 使用提前获取的account_id
            currency_id,
            amount,
            Method.TRANSFER_OUT.value,
            source,
            balance_before,
            balance_after,
        )
        try:
            await HooksManager().run_hooks(
                HooksType.POST.value,
                TransactionComplete(
                    message="交易完成",
                    source_balance=balance_before,
                    new_balance=balance_after,
                    timestamp=datetime.now().timestamp(),
                    user_id=user_id,
                ),
            )
        finally:
            return ActionResult(success=True, message="操作成功")


async def batch_add_balance(
    updates: list[tuple[str, float]],
    currency_id: str,
    source: str = "batch_update",
    session: AsyncSession | None = None,
    return_all_on_fail: bool = False,
) -> list[ActionResult]:
    """批量添加余额

    Args:
        updates (list[tuple[str, float]]): 元组列表 [(用户ID, 金额变化)]
        source (str, optional): 来源. Defaults to "batch_update".
        session (AsyncSession | None, optional): 会话. Defaults to None.
        return_all_on_fail (bool, optional): 返回所有结果即使失败时. Defaults to False.

    Returns:
        list[ActionResult]: 返回的数据（与列表顺序一致，如果任意一个失败则返回空列表）
    """
    if session is None:
        session = get_session()
    result_list: list[ActionResult] = []
    async with session:
        for uid, amount in updates:
            data: ActionResult = await add_balance(
                uid, currency_id, amount, source, session
            )
            result_list.append(data)
        if not all(r.success for r in result_list):
            return [] if not return_all_on_fail else result_list
        return result_list


async def add_balance(
    user_id: str,
    currency_id: str,
    amount: float,
    source: str = "",
    arg_session: AsyncSession | None = None,
) -> ActionResult:
    """异步增加余额

    Args:
        user_id (str): 用户ID
        currency_id (str): 货币ID
        amount (float): 金额
        source (str, optional): 来源说明. Defaults to "".
        session (AsyncSession | None, optional): 数据库异步会话. Defaults to None.

    Returns:
        ActionResult: 是否成功("success")，消息说明("message")
    """
    session = get_session() if arg_session is None else arg_session
    async with session:
        if amount <= 0:
            return ActionResult(
                success=False,
                message="金额必须大于0",
            )
        account_repo = AccountRepository(session)
        tx_repo = TransactionRepository(session)

        account = await account_repo.get_or_create_account(user_id, currency_id)
        session.add(account)
        account_id = account.id
        balance_before = account.balance
        try:
            await HooksManager().run_hooks(
                HooksType.PRE.value,
                TransactionContext(
                    user_id=user_id,
                    currency=currency_id,
                    amount=amount,
                    action_type=Method.DEPOSIT.value,
                ),
            )
        except DataUpdate as du:
            amount = du.amount
        except CancelAction as e:
            logger.warning(f"取消了交易：{e.message}")
            return ActionResult(success=True, message=f"取消了交易：{e.message}")
        balance_after = balance_before + amount
        await tx_repo.create_transaction(
            account_id,
            currency_id,
            amount,
            Method.DEPOSIT.value,
            source,
            balance_before,
            balance_after,
        )
        account = await account_repo.get_or_create_account(user_id, currency_id)
        await account_repo.update_balance(
            account.id,
            balance_after,
            currency_id,
        )
        try:
            await HooksManager().run_hooks(
                HooksType.POST.value,
                TransactionComplete(
                    message="交易完成",
                    source_balance=balance_before,
                    new_balance=balance_after,
                    timestamp=datetime.now().timestamp(),
                    user_id=user_id,
                ),
            )
        finally:
            return ActionResult(
                message="操作成功",
                success=True,
            )


async def transfer_funds(
    fromuser_id: str,
    touser_id: str,
    currency_id: str,
    amount: float,
    source: str = "transfer",
    arg_session: AsyncSession | None = None,
) -> TransferResult:
    """异步转账

    Args:
        fromuser_id (str): 源用户ID
        touser_id (str): 目标用户ID
        currency_id (str): 货币ID
        amount (float): 金额
        source (str, optional): 源说明. Defaults to "transfer".
        session (AsyncSession | None, optional): 数据库异步Session. Defaults to None.

    Returns:
        TransferResult: 如果成功则包含"from_balance"（源账户现在的balance），"to_balance"（目标账户现在的balance）字段
    """

    session = get_session() if arg_session is None else arg_session
    if amount <= 0:
        return TransferResult(
            message="金额必须大于0",
            success=False,
        )
    async with session:
        account_repo = AccountRepository(session)
        tx_repo = TransactionRepository(session)

        from_account = await account_repo.get_or_create_account(
            fromuser_id,
            currency_id,
        )
        session.add(from_account)
        to_account = await account_repo.get_or_create_account(
            touser_id,
            currency_id,
        )
        session.add(to_account)

        from_balance_before = from_account.balance
        to_balance_before = to_account.balance
        from_account_id = from_account.id
        to_account_id = to_account.id

        try:
            try:
                await HooksManager().run_hooks(
                    HooksType.PRE.value,
                    TransactionContext(
                        user_id=fromuser_id,
                        currency=currency_id,
                        amount=amount,
                        action_type=Method.TRANSFER_OUT.value,
                    ),
                )
            except DataUpdate as du:
                amount = abs(du.amount)
            try:
                await HooksManager().run_hooks(
                    HooksType.PRE.value,
                    TransactionContext(
                        user_id=touser_id,
                        currency=currency_id,
                        amount=amount,
                        action_type=Method.TRANSFER_IN.value,
                    ),
                )
            except DataUpdate as du:
                amount = abs(du.amount)
        except CancelAction as e:
            logger.info(f"取消了交易：{e.message}")
            return TransferResult(success=True, message=f"取消了交易：{e.message}")
        from_balance_before, from_balance_after = await account_repo.update_balance(
            from_account_id,
            from_balance_before - amount,
            currency_id,
        )
        to_balance_before, to_balance_after = await account_repo.update_balance(
            to_account_id,
            to_balance_before + amount,
            currency_id,
        )
        timestamp = datetime.now(timezone.utc)
        await tx_repo.create_transaction(
            account_id=from_account_id,
            currency_id=currency_id,
            amount=-amount,
            action="TRANSFER_OUT",
            source=source,
            balance_before=from_balance_before,
            balance_after=from_balance_after,
            timestamp=timestamp,
        )
        await tx_repo.create_transaction(
            account_id=to_account_id,
            currency_id=currency_id,
            amount=amount,
            action="TRANSFER_IN",
            source=source,
            balance_before=to_balance_before,
            balance_after=to_balance_after,
            timestamp=timestamp,
        )
        try:
            await HooksManager().run_hooks(
                HooksType.POST.value,
                TransactionComplete(
                    message="交易完成(转账)",
                    source_balance=from_balance_before,
                    new_balance=from_balance_after,
                    timestamp=datetime.now().timestamp(),
                    user_id=fromuser_id,
                ),
            )
            await HooksManager().run_hooks(
                HooksType.POST.value,
                TransactionComplete(
                    message="交易完成(转账)",
                    source_balance=to_balance_before,
                    new_balance=to_balance_after,
                    timestamp=datetime.now().timestamp(),
                    user_id=touser_id,
                ),
            )
        finally:
            return TransferResult(
                success=True,
                from_balance=from_balance_after,
                to_balance=to_balance_after,
                message=f"交易完成(转账) 从{fromuser_id}到{touser_id}",
            )
