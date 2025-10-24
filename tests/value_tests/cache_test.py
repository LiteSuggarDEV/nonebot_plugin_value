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
    assert (
        await (await cache_manager.get_cache(CacheCategoryEnum.CURRENCY)).get(
            data_id="1"
        )
        == TEST_CURRENCY
    )
    assert (
        await (await cache_manager.get_cache(CacheCategoryEnum.ACCOUNT)).get(
            data_id="1"
        )
    ) == TEST_USER
    assert (
        await (await cache_manager.get_cache(CacheCategoryEnum.TRANSACTION)).get(
            data_id="1"
        )
        == TEST_TRANSACTION
    )
    await cache_manager.expire_cache(category=CacheCategoryEnum.CURRENCY)
    assert not await (await cache_manager.get_cache(CacheCategoryEnum.CURRENCY)).get(
        data_id="1"
    )
    await cache_manager.expire_cache(category=CacheCategoryEnum.ACCOUNT)
    assert not await (await cache_manager.get_cache(CacheCategoryEnum.ACCOUNT)).get(
        data_id="1"
    )
    await cache_manager.expire_cache(category=CacheCategoryEnum.TRANSACTION)
    assert not await (await cache_manager.get_cache(CacheCategoryEnum.TRANSACTION)).get(
        data_id="1"
    )
    await cache_manager.expire_all_cache()
