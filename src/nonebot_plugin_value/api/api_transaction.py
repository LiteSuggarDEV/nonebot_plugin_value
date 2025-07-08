from ..db_api.transaction import get_transaction_history as _transaction_history
from ..db_api.transaction import remove_transaction as _remove_transaction
from ..pyd_models.transaction_pyd import TransactionData


async def get_transaction_history(
    account_id: str,
    limit: int = 10,
) -> list[TransactionData]:
    """获取账户历史交易记录

    Args:
        account_id (str): 账户ID
        limit (int, optional): 最大数量. Defaults to 10.

    Returns:
        list[TransactionData]: 包含交易数据的列表
    """
    return [
        TransactionData.model_validate(transaction)
        for transaction in await _transaction_history(account_id, limit)
    ]


async def remove_transaction(transaction_id: str) -> bool:
    """删除交易记录

    Args:
        transaction_id (str): 交易ID

    Returns:
        bool: 是否成功删除
    """
    return await _remove_transaction(transaction_id)
