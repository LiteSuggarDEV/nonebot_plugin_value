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
async def test_depends(app: App):
    from nonebot_plugin_value.api.api_balance import (
        del_account,
        get_or_create_account,
    )
    from nonebot_plugin_value.api.depends.factory import DependsSwitch
    from nonebot_plugin_value.uuid_lib import to_uuid

    uid = to_uuid("123456789")

    # 创建账户并验证初始状态
    account = await get_or_create_account(uid)
    assert account.balance == 0.0, f"账户初始余额应为 0.0，实际为 {account.balance}"

    # 使用依赖注入获取执行器
    executor = await (DependsSwitch().account_executor())(make_event())

    # 添加余额
    await executor.add_balance(100)

    # 验证余额（通过执行器）
    balance_via_executor = await executor.get_balance()
    assert balance_via_executor == 100.0, (
        f"通过执行器获取的余额应为 100.0，实际为 {balance_via_executor}"
    )

    # 再次验证余额（通过 API）
    account_after_add = await get_or_create_account(uid)
    assert account_after_add.balance == 100.0, (
        f"通过 API 获取的余额应为 100.0，实际为 {account_after_add.balance}"
    )

    # 清理账户
    delete_result = await del_account(uid)
    assert delete_result, "账户应该被成功删除"
