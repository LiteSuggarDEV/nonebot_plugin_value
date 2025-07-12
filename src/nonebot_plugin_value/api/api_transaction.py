from nonebot_plugin_orm import get_session

from ..pyd_models.transaction_pyd import TransactionData
from ..services.transaction import get_transaction_history as _transaction_history
from ..services.transaction import remove_transaction as _remove_transaction


async def get_transaction_history(
    account_id: str,
    limit: int = 10,
) -> list[TransactionData]:
    """获取账户历史交易记录

    Args:
        account_id (str): 账户ID
        limit (int, optional): 数量. Defaults to 10.

    Returns:
        list[TransactionData]: 包含交易数据的列表
    """
    async with get_session() as session:
        return [
            TransactionData(
                id=transaction.id,
                account_id=transaction.account_id,
                currency_id=transaction.currency_id,
                amount=transaction.amount,
                action=transaction.action,
                source=transaction.source,
                balance_before=transaction.balance_before,
                balance_after=transaction.balance_after,
                timestamp=transaction.timestamp,
            )
            for transaction in await _transaction_history(
                account_id,
                session,
                limit,
            )
        ]


async def remove_transaction(transaction_id: str) -> bool:
    """删除交易记录

    Args:
        transaction_id (str): 交易ID

    Returns:
        bool: 是否成功删除
    """
    async with get_session() as session:
        return await _remove_transaction(
            transaction_id,
            session,
        )
