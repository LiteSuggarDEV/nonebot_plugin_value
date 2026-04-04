import pytest
from nonebug import App  # type:ignore


@pytest.mark.asyncio
async def test_transfer(app: App):
    from nonebot_plugin_value.api.api_balance import (
        add_balance,
        get_or_create_account,
        transfer_funds,
    )
    from nonebot_plugin_value.uuid_lib import to_uuid

    u1 = to_uuid("u1")
    u2 = to_uuid("u2")

    # 创建账户
    account1 = await get_or_create_account(u1)
    account2 = await get_or_create_account(u2)
    assert account1.balance == 0.0, (
        f"账户 u1 初始余额应为 0.0，实际为 {account1.balance}"
    )
    assert account2.balance == 0.0, (
        f"账户 u2 初始余额应为 0.0，实际为 {account2.balance}"
    )

    # 添加余额
    await add_balance(u1, 100)
    account1_after_add = await get_or_create_account(u1)
    assert account1_after_add.balance == 100.0, (
        f"充值后 u1 余额应为 100.0，实际为 {account1_after_add.balance}"
    )

    # 转账
    await transfer_funds(u1, u2, 50)

    # 验证转账后的余额
    account1_after_transfer = await get_or_create_account(u1)
    account2_after_transfer = await get_or_create_account(u2)

    assert account1_after_transfer.balance == 50.0, (
        f"转账后 u1 余额应为 50.0，实际为 {account1_after_transfer.balance}"
    )
    assert account2_after_transfer.balance == 50.0, (
        f"转账后 u2 余额应为 50.0，实际为 {account2_after_transfer.balance}"
    )
