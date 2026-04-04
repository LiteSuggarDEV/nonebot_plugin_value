import pytest
from nonebug import App  # type:ignore


@pytest.mark.asyncio
async def test_batch_operations(app: App):
    from nonebot_plugin_value.api.api_balance import (
        batch_add_balance,
        batch_del_balance,
        del_account,
        get_or_create_account,
        list_accounts,
    )
    from nonebot_plugin_value.api.api_currency import (
        CurrencyData,
        get_or_create_currency,
        list_currencies,
    )
    from nonebot_plugin_value.uuid_lib import to_uuid

    ac_uid: list[str] = [to_uuid(f"account{i}") for i in range(10)]
    cu_id = to_uuid("currency")
    cu_data = CurrencyData(id=cu_id, display_name="currency", symbol="C")
    await get_or_create_currency(cu_data)
    for uid in ac_uid:
        await get_or_create_account(uid)
        await get_or_create_account(uid, cu_id)

    # 批量添加余额（默认货币）
    await batch_add_balance(
        [(uid, 1) for uid in ac_uid],
    )

    # 验证默认货币余额是否都成功增加了 1
    for uid in ac_uid:
        account = await get_or_create_account(uid)
        assert account.balance == 1.0, (
            f"账户 {uid} 的默认货币余额应为 1.0，实际为 {account.balance}"
        )

    # 批量添加余额（指定货币）
    await batch_add_balance(
        [(uid, 1) for uid in ac_uid],
        currency_id=cu_id,
    )

    # 验证指定货币余额是否都成功增加了 1
    for uid in ac_uid:
        account = await get_or_create_account(uid, cu_id)
        assert account.balance == 1.0, (
            f"账户 {uid} 的指定货币余额应为 1.0，实际为 {account.balance}"
        )

    # 再次批量添加以验证累加
    await batch_add_balance(
        [(uid, 2) for uid in ac_uid],
    )

    # 验证默认货币余额是否都成功累加到 3.0 (1 + 2)
    for uid in ac_uid:
        account = await get_or_create_account(uid)
        assert account.balance == 3.0, (
            f"账户 {uid} 的默认货币余额应为 3.0，实际为 {account.balance}"
        )

    # 批量减少余额
    await batch_del_balance(
        [(uid, 1) for uid in ac_uid],
    )

    # 验证默认货币余额是否都成功减少到 2.0 (3 - 1)
    for uid in ac_uid:
        account = await get_or_create_account(uid)
        assert account.balance == 2.0, (
            f"账户 {uid} 的默认货币余额应为 2.0，实际为 {account.balance}"
        )

    # 批量减少余额（指定货币）
    await batch_del_balance(
        [(uid, 1) for uid in ac_uid],
        currency_id=cu_id,
    )

    # 验证指定货币余额是否都成功减少到 0.0 (1 - 1)
    for uid in ac_uid:
        account = await get_or_create_account(uid, cu_id)
        assert account.balance == 0.0, (
            f"账户 {uid} 的指定货币余额应为 0.0，实际为 {account.balance}"
        )

    # 测试列表功能
    await list_accounts()

    # 删除所有账户并验证删除成功
    delete_results = [await del_account(uid) for uid in ac_uid]
    assert all(delete_results), "所有账户应该被成功删除"

    # 验证货币列表功能
    await list_currencies()
