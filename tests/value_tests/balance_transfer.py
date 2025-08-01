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
    await get_or_create_account(u1)
    await get_or_create_account(u2)
    await add_balance(u1, 100)
    assert (await transfer_funds(u1, u2, 50)).balance == 50
