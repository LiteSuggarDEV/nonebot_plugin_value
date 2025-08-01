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
    await get_or_create_account(account)
    await add_balance(
        account,
        100,
        "add",
    )
    await del_balance(
        account,
        100,
        "del",
    )
    assert await del_account(account)
