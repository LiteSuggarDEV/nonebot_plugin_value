import pytest
from nonebug import App  # type: ignore


@pytest.mark.asyncio
async def test_new_currency(app: App):
    from nonebot_plugin_value.api.api_balance import (
        add_balance,
        del_account,
        del_balance,
        get_or_create_account,
    )
    from nonebot_plugin_value.api.api_currency import (
        CurrencyData,
        get_currency,
        get_or_create_currency,
        remove_currency,
    )
    from nonebot_plugin_value.uuid_lib import to_uuid

    c_id = "114514"
    u_id = to_uuid("114514")

    # 创建货币
    currency = CurrencyData(id=c_id, display_name="test", symbol="t")
    created_currency = await get_or_create_currency(currency)
    assert created_currency.id == c_id, (
        f"创建的货币 ID 应为 {c_id}，实际为 {created_currency.id}"
    )
    assert created_currency.display_name == "test", (
        f"货币名称应为 'test'，实际为 {created_currency.display_name}"
    )

    # 验证货币存在
    currency_data = await get_currency(c_id)
    assert currency_data is not None, "货币应该存在"
    assert currency_data.id == c_id, "获取的货币 ID 应该与创建的一致"

    # 创建账户
    account = await get_or_create_account(u_id, c_id)
    assert account.currency_id == c_id, (
        f"账户货币 ID 应为 {c_id}，实际为 {account.currency_id}"
    )
    assert account.balance == 0.0, f"账户初始余额应为 0.0，实际为 {account.balance}"

    # 添加余额
    await add_balance(u_id, 114514, "1919810", c_id)
    account_after_add = await get_or_create_account(u_id, c_id)
    assert account_after_add.balance == 114514.0, (
        f"充值后余额应为 114514.0，实际为 {account_after_add.balance}"
    )

    # 减少余额
    await del_balance(u_id, 114514, "1919810", c_id)
    account_after_del = await get_or_create_account(u_id, c_id)
    assert account_after_del.balance == 0.0, (
        f"扣减后余额应为 0.0，实际为 {account_after_del.balance}"
    )

    # 删除账户
    delete_result = await del_account(u_id, c_id)
    assert delete_result, "账户应该被成功删除"

    # 删除货币
    await remove_currency(c_id)

    # 验证货币不存在
    currency_after_remove = await get_currency(c_id)
    assert currency_after_remove is None, "货币删除后应该不存在"
