import pytest
from nonebug import App  # type:ignore


@pytest.mark.asyncio
async def test_cache(app: App):
    from nonebot_plugin_value._cache import CacheCategoryEnum, CacheManager
    from nonebot_plugin_value.pyd_models.balance_pyd import UserAccountData
    from nonebot_plugin_value.pyd_models.currency_pyd import CurrencyData
    from nonebot_plugin_value.pyd_models.transaction_pyd import TransactionData

    TEST_CURRENCY = CurrencyData(id="1", display_name="test", symbol="t")
    TEST_USER = UserAccountData(id="1", uni_id="1", currency_id="1")
    TEST_TRANSACTION = TransactionData(id="1", source="test", amount=1, currency_id="1")
    cache_manager = CacheManager()

    # 测试缓存更新
    await cache_manager.update_cache(
        category=CacheCategoryEnum.CURRENCY,
        data=TEST_CURRENCY,
    )
    await cache_manager.update_cache(
        category=CacheCategoryEnum.ACCOUNT,
        data=TEST_USER,
    )
    await cache_manager.update_cache(
        category=CacheCategoryEnum.TRANSACTION,
        data=TEST_TRANSACTION,
    )

    # 验证缓存命中
    currency_cache = await (
        await cache_manager.get_cache(CacheCategoryEnum.CURRENCY)
    ).get(data_id="1")
    assert currency_cache == TEST_CURRENCY, "货币缓存应该与测试数据一致"

    user_cache = await (await cache_manager.get_cache(CacheCategoryEnum.ACCOUNT)).get(
        data_id="1"
    )
    assert user_cache == TEST_USER, "用户缓存应该与测试数据一致"

    transaction_cache = await (
        await cache_manager.get_cache(CacheCategoryEnum.TRANSACTION)
    ).get(data_id="1")
    assert transaction_cache == TEST_TRANSACTION, "交易缓存应该与测试数据一致"

    # 测试缓存过期
    await cache_manager.expire_cache(category=CacheCategoryEnum.CURRENCY)
    assert not await (await cache_manager.get_cache(CacheCategoryEnum.CURRENCY)).get(
        data_id="1"
    ), "货币缓存过期后应该不存在"

    await cache_manager.expire_cache(category=CacheCategoryEnum.ACCOUNT)
    assert not await (await cache_manager.get_cache(CacheCategoryEnum.ACCOUNT)).get(
        data_id="1"
    ), "用户缓存过期后应该不存在"

    await cache_manager.expire_cache(category=CacheCategoryEnum.TRANSACTION)
    assert not await (await cache_manager.get_cache(CacheCategoryEnum.TRANSACTION)).get(
        data_id="1"
    ), "交易缓存过期后应该不存在"

    # 测试清空所有缓存
    await cache_manager.update_cache(
        category=CacheCategoryEnum.CURRENCY,
        data=TEST_CURRENCY,
    )
    await cache_manager.expire_all_cache()
    assert not await (await cache_manager.get_cache(CacheCategoryEnum.CURRENCY)).get(
        data_id="1"
    ), "清空所有缓存后应该不存在"
