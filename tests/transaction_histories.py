import pytest
from nonebug import App  # type: ignore


@pytest.mark.asyncio
async def test_transactions(app: App):
    from nonebot_plugin_value.api.api_balance import add_balance, get_or_create_account
    from nonebot_plugin_value.api.api_transaction import get_transaction_history
    from nonebot_plugin_value.uuid_lib import to_uuid

    account_id = to_uuid("123")

    # 创建账户并验证初始状态
    account = await get_or_create_account(account_id)
    assert account.balance == 0.0, f"账户初始余额应为 0.0，实际为 {account.balance}"

    # 多次添加余额
    for i in range(20):
        await add_balance(account_id, 1)

    # 验证最终余额
    account_after_adds = await get_or_create_account(account_id)
    assert account_after_adds.balance == 20.0, (
        f"20 次充值后余额应为 20.0，实际为 {account_after_adds.balance}"
    )

    # 获取交易历史
    transactions = await get_transaction_history(account.id, 30)

    # 验证交易记录数量和完整性
    assert len(transactions) >= 20, (
        f"交易记录数量应该至少 20 条，实际为 {len(transactions)} 条"
    )

    # 验证每笔交易的金额（应该是 1）
    for i, transaction in enumerate(transactions[:20]):
        assert transaction.amount == 1, (
            f"第 {i + 1} 笔交易金额应为 1，实际为 {transaction.amount}"
        )

    # 验证交易记录的连续性（可选）
    if len(transactions) > 1:
        # 检查交易记录是否按时间倒序排列（最新的在前）
        for i in range(len(transactions) - 1):
            assert transactions[i].timestamp >= transactions[i + 1].timestamp, (
                "交易记录应该按时间倒序排列"
            )
