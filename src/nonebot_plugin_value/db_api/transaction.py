from nonebot_plugin_orm import AsyncSession

from ..repository import TransactionRepository


async def get_transaction_history(
    account_id: str,
    session: AsyncSession,
    limit: int = 100,
):
    """获取一个用户的交易记录

    Args:
        session (AsyncSession | None, optional): 异步数据库会话
        account_id (str): 用户UUID(应自行处理)
        limit (int, optional): 数据条数. Defaults to 100.

    Returns:
        Sequence[Transaction]: 记录列表
    """
    return await TransactionRepository(session).get_transaction_history(
        account_id, limit
    )


async def remove_transaction(
    transaction_id: str,
    session: AsyncSession,
    fail_then_throw: bool = False,
) -> bool:
    """删除交易记录

    Args:
        transaction_id (str): 交易ID
        session (AsyncSession | None, optional): 异步数据库会话. Defaults to None.
        fail_then_throw (bool, optional): 如果失败则抛出异常. Defaults to False.

    Returns:
        bool: 是否成功
    """
    async with session:
        try:
            await TransactionRepository(session).remove_transaction(transaction_id)
            return True
        except Exception:
            await session.rollback()
            if fail_then_throw:
                raise
            return False
