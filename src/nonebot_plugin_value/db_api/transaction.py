from nonebot_plugin_orm import AsyncSession, get_session

from ..repository import TransactionRepository


async def get_transaction_history(
    account_id: str,
    limit: int = 100,
    session: AsyncSession | None = None,
):
    """获取一个用户的交易记录

    Args:
        session (AsyncSession | None, optional): 异步数据库会话
        account_id (str): 用户UUID(应自行处理)
        limit (int, optional): 数据条数. Defaults to 100.

    Returns:
        Sequence[Transaction]: 记录列表
    """
    if session is None:
        session = get_session()
    return await TransactionRepository(session).get_transaction_history(
        account_id, limit
    )
