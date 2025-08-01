import pytest
from nonebug import App  # type: ignore


@pytest.mark.asyncio
async def test_transactions(app: App):
    from nonebot_plugin_value.api.api_balance import add_balance, get_or_create_account
    from nonebot_plugin_value.api.api_transaction import get_transaction_history
    from nonebot_plugin_value.uuid_lib import to_uuid

    account = await get_or_create_account(to_uuid("123"))
    for _ in range(20):
        await add_balance(to_uuid("123"), 1)
    transactions = await get_transaction_history(account.id,30)
    assert len(transactions) >= 20
    assert transactions[0].amount == 1
