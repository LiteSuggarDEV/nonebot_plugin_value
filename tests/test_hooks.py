import pytest
from nonebug import App  # type:ignore


@pytest.mark.asyncio
async def test_hooks_manager(app: App):
    """测试钩子管理器功能"""
    from nonebot_plugin_value.hook.context import (
        TransactionComplete,
        TransactionContext,
    )
    from nonebot_plugin_value.hook.exception import CancelAction, DataUpdate
    from nonebot_plugin_value.hook.hooks_manager import HooksManager
    from nonebot_plugin_value.hook.hooks_type import HooksType

    # 获取单例实例
    manager = HooksManager()

    # 测试 Hook 类型枚举
    assert HooksType.pre() == "vault_pre_transaction"
    assert HooksType.post() == "vault_post_transaction"
    assert len(HooksType.methods()) == 2
    assert "vault_pre_transaction" in HooksType.methods()
    assert "vault_post_transaction" in HooksType.methods()

    # 清理可能存在的旧钩子
    setattr(manager, "_HooksManager__hooks", {})

    # 测试注册钩子
    pre_hook_called = False
    post_hook_called = False

    async def pre_transaction_hook(context: TransactionContext):
        nonlocal pre_hook_called
        pre_hook_called = True
        assert getattr(context, "user_id") == "test_user"
        assert getattr(context, "currency") == "test_currency"
        assert getattr(context, "amount") == 100.0
        assert getattr(context, "action_type") == "add_balance"

    async def post_transaction_hook(context: TransactionComplete):
        nonlocal post_hook_called
        post_hook_called = True
        assert getattr(context, "message") == "Transaction completed"
        assert getattr(context, "source_balance") == 0.0
        assert getattr(context, "new_balance") == 100.0
        assert getattr(context, "user_id") == "test_user"

    # 使用 register 方法注册
    manager.register(HooksType.pre(), pre_transaction_hook)
    manager.register(HooksType.post(), post_transaction_hook)

    # 验证钩子已注册
    hooks_dict = getattr(manager, "_HooksManager__hooks")
    assert HooksType.pre() in hooks_dict
    assert HooksType.post() in hooks_dict
    assert len(hooks_dict[HooksType.pre()]) == 1
    assert len(hooks_dict[HooksType.post()]) == 1

    # 测试运行 PRE 钩子
    pre_context = TransactionContext(
        user_id="test_user",
        currency="test_currency",
        amount=100.0,
        action_type="add_balance",
    )
    await manager.run_hooks(HooksType.pre(), pre_context)
    assert pre_hook_called, "PRE 钩子应该被调用"

    # 测试运行 POST 钩子
    post_context = TransactionComplete(
        message="Transaction completed",
        source_balance=0.0,
        new_balance=100.0,
        user_id="test_user",
    )
    await manager.run_hooks(HooksType.post(), post_context)
    assert post_hook_called, "POST 钩子应该被调用"

    # 测试装饰器方式注册
    decorator_hook_called = False

    @manager.on_event(HooksType.pre())
    async def decorator_hook(context: TransactionContext):  # type: ignore[reportUnusedFunction]
        """装饰器方式注册的钩子函数"""
        nonlocal decorator_hook_called
        decorator_hook_called = True

    # 验证装饰器注册的钩子存在
    hooks_dict = getattr(manager, "_HooksManager__hooks")
    assert len(hooks_dict[HooksType.pre()]) == 2

    # 运行所有 PRE 钩子（包括装饰器注册的）
    pre_hook_called = False
    decorator_hook_called = False
    await manager.run_hooks(HooksType.pre(), pre_context)
    assert pre_hook_called, "第一个 PRE 钩子应该被调用"
    assert decorator_hook_called, "装饰器注册的 PRE 钩子应该被调用"

    # 测试无效钩子名称
    with pytest.raises(ValueError, match="Invalid hook name"):
        manager.register("invalid_hook_name", pre_transaction_hook)

    # 测试取消操作
    async def cancel_hook(context: TransactionContext):
        context.cancel("Test cancel reason")

    setattr(manager, "_HooksManager__hooks", {})
    manager.register(HooksType.pre(), cancel_hook)

    with pytest.raises(CancelAction) as exc_info:
        await manager.run_hooks(HooksType.pre(), pre_context)

    assert str(exc_info.value) == "Test cancel reason"

    # 测试数据更新
    async def update_hook(context: TransactionContext):
        context.commit_update()

    setattr(manager, "_HooksManager__hooks", {})
    manager.register(HooksType.pre(), update_hook)

    with pytest.raises(DataUpdate) as exc_info:
        await manager.run_hooks(HooksType.pre(), pre_context)

    assert getattr(exc_info.value, "amount") == 100.0

    # 测试不存在的钩子（应该直接返回，不执行任何操作）
    setattr(manager, "_HooksManager__hooks", {})
    await manager.run_hooks(HooksType.pre(), pre_context)  # 不应该抛出异常

    # 测试钩子执行异常处理
    error_hook_called = False

    async def error_hook(context: TransactionContext):
        nonlocal error_hook_called
        error_hook_called = True
        raise ValueError("Test error in hook")

    setattr(manager, "_HooksManager__hooks", {})
    manager.register(HooksType.pre(), error_hook)

    with pytest.raises(ValueError, match="Test error in hook"):
        await manager.run_hooks(HooksType.pre(), pre_context)
    assert error_hook_called, "错误的钩子也应该被调用"
