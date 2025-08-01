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
    currency = CurrencyData(id=c_id, display_name="test", symbol="t")
    await get_or_create_currency(currency)
    await get_or_create_account(u_id, c_id)
    await add_balance(u_id, 114514, "1919810", c_id)
    await del_balance(u_id, 114514, "1919810", c_id)
    assert await del_account(u_id, c_id)
    await remove_currency(c_id)
    assert not await get_currency(c_id)
