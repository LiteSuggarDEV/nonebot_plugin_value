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

    ac_uid: list[str] = [to_uuid(f"account{i}") for i in range(100)]
    cu_id = to_uuid("currency")
    cu_data = CurrencyData(id=cu_id, display_name="currency", symbol="C")
    await get_or_create_currency(cu_data)
    for uid in ac_uid:
        await get_or_create_account(uid)
        await get_or_create_account(uid, cu_id)
    await batch_add_balance(
        [(uid, 1) for uid in ac_uid],
    )
    await batch_add_balance(
        [(uid, 1) for uid in ac_uid],
        currency_id=cu_id,
    )
    await batch_del_balance(
        [(uid, 1) for uid in ac_uid],
    )
    await batch_del_balance(
        [(uid, 1) for uid in ac_uid],
        currency_id=cu_id,
    )
    await list_accounts()
    assert all([await del_account(uid) for uid in ac_uid])
    await list_currencies()

