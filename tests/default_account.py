import pytest
from nonebug import App  # type: ignore


@pytest.mark.asyncio
async def test_balance(app: App):
    from nonebot_plugin_value.api.api_balance import (
        add_balance,
        del_account,
        del_balance,
        get_or_create_account,
    )
    from nonebot_plugin_value.uuid_lib import to_uuid

    account = to_uuid("Test_Example")

    # 创建账户并验证初始状态
    created_account = await get_or_create_account(account)
    assert created_account.balance == 0.0, (
        f"账户初始余额应为 0.0，实际为 {created_account.balance}"
    )

    # 添加余额
    await add_balance(
        account,
        100,
        "add",
    )
    account_after_add = await get_or_create_account(account)
    assert account_after_add.balance == 100.0, (
        f"充值后余额应为 100.0，实际为 {account_after_add.balance}"
    )

    # 减少余额
    await del_balance(
        account,
        100,
        "del",
    )
    account_after_del = await get_or_create_account(account)
    assert account_after_del.balance == 0.0, (
        f"扣减后余额应为 0.0，实际为 {account_after_del.balance}"
    )

    # 删除账户并验证
    delete_result = await del_account(account)
    assert delete_result, "账户应该被成功删除"
