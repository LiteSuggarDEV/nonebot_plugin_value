import pytest
from nonebug import App  # type: ignore


def make_event():
    from nonebot.adapters.onebot.v11 import Message, MessageEvent
    from nonebot.adapters.onebot.v11.event import Sender

    return MessageEvent(
        time=0,
        self_id=0,
        user_id=123456789,
        post_type="message",
        message=Message(""),
        sub_type="friend",
        message_type="private",
        message_id=0,
        raw_message="",
        font=0,
        sender=Sender(),
        original_message=Message(),
    )


@pytest.mark.asyncio
async def test_new_currency(app: App):
    from nonebot_plugin_value.api.api_balance import del_account
    from nonebot_plugin_value.api.depends.factory import DependsSwitch
    from nonebot_plugin_value.uuid_lib import to_uuid

    uid = to_uuid("123456789")
    executor = await (DependsSwitch().account_executor())(make_event())
    await executor.add_balance(100)
    assert await executor.get_balance() == 100
    await del_account(uid)
