import asyncio

import pytest
from nonebug import App  # type:ignore


@pytest.mark.asyncio
async def test_currency_api(app: App):
    """测试货币 API 的完整功能"""
    from nonebot_plugin_value.api.api_currency import (
        create_currency,
        get_currency,
        get_currency_by_kwargs,
        get_default_currency,
        list_currencies,
        remove_currency,
        update_currency,
    )
    from nonebot_plugin_value.pyd_models.currency_pyd import CurrencyData
    from nonebot_plugin_value.uuid_lib import to_uuid

    # 测试获取默认货币
    default_currency = await get_default_currency()
    assert default_currency is not None, "应该存在默认货币"
    assert default_currency.id is not None, "默认货币应该有 ID"

    # 测试创建新货币
    test_currency_id = to_uuid("test_api_currency")
    new_currency_data = CurrencyData(
        id=test_currency_id, display_name="Test API Currency", symbol="TAC"
    )
    await create_currency(new_currency_data)

    # 验证创建成功
    currency = await get_currency(test_currency_id)
    assert currency is not None, "货币应该被创建"
    assert currency.display_name == "Test API Currency", "货币名称应该匹配"
    assert currency.symbol == "TAC", "货币符号应该匹配"

    # 测试通过 kwargs 查询
    currency_by_kwargs = await get_currency_by_kwargs(display_name="Test API Currency")
    assert currency_by_kwargs is not None, "应该能通过 kwargs 查询到货币"
    assert currency_by_kwargs.id == test_currency_id, "查询结果应该匹配"

    # 测试不存在的 kwargs 查询
    not_found = await get_currency_by_kwargs(display_name="Non Existent Currency")
    assert not_found is None, "不存在的货币应该返回 None"

    # 测试更新货币
    updated_currency_data = CurrencyData(
        id=test_currency_id, display_name="Updated Test Currency", symbol="UTC"
    )
    updated_currency = await update_currency(updated_currency_data)
    assert updated_currency.display_name == "Updated Test Currency", (
        "货币名称应该被更新"
    )
    assert updated_currency.symbol == "UTC", "货币符号应该被更新"

    # 验证更新持久化（强制从数据库读取，不使用缓存）
    currency_after_update = await get_currency(test_currency_id, no_cache=True)
    assert currency_after_update is not None, "更新后的货币应该存在"
    assert currency_after_update.display_name == "Updated Test Currency", (
        "更新应该持久化"
    )
    # 测试获取所有货币
    currencies = await list_currencies()
    assert len(currencies) >= 2, "应该至少有两个货币（默认 + 测试）"

    # 测试 no_cache_update 参数
    currencies_no_cache = await list_currencies(no_cache_update=True)
    assert len(currencies_no_cache) >= 2, "即使不更新缓存也应该返回数据"

    # 测试缓存命中
    cached_currency = await get_currency(test_currency_id, no_cache=False)
    assert cached_currency is not None, "应该能从缓存获取货币"

    # 测试 no_cache 参数（强制不使用缓存）
    no_cache_currency = await get_currency(test_currency_id, no_cache=True)
    assert no_cache_currency is not None, "即使不使用缓存也应该能获取货币"

    # 测试删除货币
    await remove_currency(test_currency_id)

    # 验证删除成功
    deleted_currency = await get_currency(test_currency_id)
    assert deleted_currency is None, "货币应该被删除"

    # 测试获取不存在的货币
    non_existent = await get_currency(to_uuid("non_existent"))
    assert non_existent is None, "不存在的货币应该返回 None"


@pytest.mark.asyncio
async def test_transaction_api(app: App):
    """测试交易记录 API"""
    import time

    from nonebot_plugin_value.api.api_balance import add_balance, get_or_create_account
    from nonebot_plugin_value.api.api_transaction import (
        get_transaction_history,
        get_transaction_history_by_time_range,
        remove_transaction,
    )
    from nonebot_plugin_value.uuid_lib import to_uuid

    test_user_id = to_uuid("test_transaction_api_user")

    # 创建账户
    await get_or_create_account(test_user_id)

    # 添加多笔余额以创建交易记录
    for i in range(5):
        await add_balance(test_user_id, 10.0 * (i + 1), f"test_add_{i}")

    # 等待一小段时间以确保时间戳不同
    await asyncio.sleep(0.01)
    timestamp_before_sleep = time.time()
    await asyncio.sleep(0.01)

    # 获取交易历史（限制数量）
    transactions_limited = await get_transaction_history(test_user_id, limit=3)
    assert len(transactions_limited) <= 3, "交易记录数量不应该超过限制"

    # 获取更多交易记录
    transactions_all = await get_transaction_history(test_user_id, limit=100)
    assert len(transactions_all) >= 5, "应该至少有 5 条交易记录"

    # 验证交易记录的属性
    for tx in transactions_all:
        assert tx.amount > 0, "充值金额应该大于 0"
        assert tx.account_id == test_user_id, "交易记录应该属于正确的账户"
        assert tx.source.startswith("test_add_"), "交易来源应该匹配"

    # 测试按时间范围查询
    transactions_by_time = await get_transaction_history_by_time_range(
        account_id=test_user_id,
        start_time=0,  # 从 Unix 纪元开始
        end_time=timestamp_before_sleep + 10,  # 到当前时间之后
        limit=10,
    )
    assert len(transactions_by_time) >= 5, "应该能找到至少 5 条交易记录"

    # 测试空的时间范围
    empty_transactions = await get_transaction_history_by_time_range(
        account_id=test_user_id,
        start_time=9999999999,  # 未来时间
        end_time=9999999999,
        limit=10,
    )
    assert len(empty_transactions) == 0, "未来时间范围应该没有交易记录"

    # 测试删除交易记录（可选，如果需要测试的话）
    if len(transactions_all) > 0:
        first_tx_id = transactions_all[0].id
        await remove_transaction(first_tx_id)
