from datetime import datetime

from nonebot_plugin_orm import get_session

from ..pyd_models.transaction_pyd import TransactionData
from ..services.transaction import get_transaction_history as _transaction_history
from ..services.transaction import (
    get_transaction_history_by_time_range as _transaction_history_by_time_range,
)
from ..services.transaction import remove_transaction as _remove_transaction


async def get_transaction_history_by_time_range(
    account_id: str,
    start_time: float,
    end_time: float,
    limit: int = 10,
) -> list[TransactionData]:
    """通过时间范围获取交易记录

    Args:
        account_id (str): 账户ID
        start_time (datetime): 开始时间
        end_time (datetime): 结束时间
        limit (int, optional): 最大记录数. Defaults to 10.

    Returns:
        list[TransactionData]: 交易记录
    """
    async with get_session() as session:
        data = await _transaction_history_by_time_range(
            account_id,
            datetime.fromtimestamp(start_time),
            datetime.fromtimestamp(end_time),
            session,
            limit,
        )
        result_list: list[TransactionData] = [
            TransactionData.model_validate(transaction, from_attributes=True)
            for transaction in data
        ]
        return result_list


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
            TransactionData.model_validate(transaction, from_attributes=True)
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
