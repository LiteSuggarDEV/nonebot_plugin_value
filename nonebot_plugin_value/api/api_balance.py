import typing

from nonebot_plugin_orm import get_session

from .._cache import CacheCategoryEnum, CacheManager
from ..pyd_models.balance_pyd import UserAccountData
from ..services.balance import add_balance as _a_balance
from ..services.balance import batch_add_balance as _batch_add
from ..services.balance import batch_del_balance as _batch_del
from ..services.balance import del_account as _del_account
from ..services.balance import del_balance as _d_balance
from ..services.balance import get_or_create_account as _go_account
from ..services.balance import list_accounts as _list_accounts
from ..services.balance import set_frozen as _set_frozen
from ..services.balance import set_frozen_all as _set_frozen_all
from ..services.balance import transfer_funds as _transfer
from ..uuid_lib import DEFAULT_CURRENCY_UUID, get_uni_id


async def set_frozen_all(account_id: str, frozen: bool) -> None:
    """冻结账户的所有货币资产

    Args:
        account_id (str): 账户ID
        frozen (bool): 是否冻结
    """
    async with get_session() as session:
        await CacheManager().expire_cache(
            category=CacheCategoryEnum.ACCOUNT, data_id=account_id
        )
        await _set_frozen_all(account_id, frozen, session)


async def set_frozen(account_id: str, currency_id: str, frozen: bool) -> None:
    """设置账户特定货币冻结状态

    Args:
        account_id (str): 用户ID
        currency_id (str): 货币ID
        frozen (bool): 是否冻结
    """
    async with get_session() as session:
        await CacheManager().expire_cache(
            category=CacheCategoryEnum.ACCOUNT,
            data_id=get_uni_id(account_id, currency_id),
        )
        await _set_frozen(account_id, frozen, currency_id, session)


async def list_accounts(
    currency_id: str | None = None, no_cache_refresh: bool = False
) -> list[UserAccountData]:
    """获取指定货币（或默认）的账户列表（无法命中缓存，但是可以更新缓存）

    Args:
        currency_id (str | None, optional): 货币ID. Defaults to None.

    Returns:
        list[UserAccountData]: 包含用户数据的列表
    """
    if currency_id is None:
        currency_id = DEFAULT_CURRENCY_UUID.hex
    async with get_session() as session:
        result = [
            UserAccountData(
                id=account.id,
                uni_id=account.uni_id,
                currency_id=account.currency_id,
                balance=account.balance,
                last_updated=account.last_updated,
            )
            for account in await _list_accounts(session, currency_id)
        ]
        if not no_cache_refresh:
            for account in result:
                await CacheManager().update_cache(
                    category=CacheCategoryEnum.ACCOUNT,
                    data=account,
                )
        return result


async def del_account(user_id: str, currency_id: str | None = None) -> bool:
    """删除账户

    Args:
        user_id (str): 用户ID
        currency_id (str | None, optional): 货币ID(不填则使用默认货币). Defaults to None.

    Returns:
        bool: 是否成功
    """
    if currency_id is None:
        currency_id = DEFAULT_CURRENCY_UUID.hex
    await CacheManager().expire_cache(
        category=CacheCategoryEnum.ACCOUNT, data_id=user_id
    )
    return await _del_account(user_id, currency_id=currency_id)


async def get_or_create_account(
    user_id: str,
    currency_id: str | None = None,
    no_cache_use: bool = False,
    no_cache_refresh: bool = False,
) -> UserAccountData:
    """获取账户数据（不存在就创建）

    Args:
        user_id (str): 用户ID
        currency_id (str | None, optional): 货币ID(不填则使用默认货币)

    Returns:
        UserAccountData: 用户数据
    """
    cache_manager = CacheManager()
    if currency_id is None:
        currency_id = DEFAULT_CURRENCY_UUID.hex
    if not no_cache_use:
        if (
            result := await (
                await cache_manager.get_cache(category=CacheCategoryEnum.ACCOUNT)
            ).get(data_id=user_id)
            is not None
        ):
            return typing.cast(UserAccountData, result)
    async with get_session() as session:
        data = await _go_account(user_id, currency_id, session)
        session.add(data)
        data = UserAccountData.model_validate(data, from_attributes=True)
        if not no_cache_refresh:
            await cache_manager.update_cache(
                category=CacheCategoryEnum.ACCOUNT,
                data=data,
            )
        return data


async def batch_del_balance(
    updates: list[tuple[str, float]],
    currency_id: str | None = None,
    source: str = "batch_update",
) -> list[UserAccountData] | None:
    """批量减少账户余额

    Args:
        updates (list[tuple[str, float]]): 元组列表，包含用户id和金额
        currency_id (str | None, optional): 货币ID. Defaults to None.
        source (str, optional): 源说明. Defaults to "batch_update".

    Returns:
        None: None
    """
    if currency_id is None:
        currency_id = DEFAULT_CURRENCY_UUID.hex
    await _batch_del(updates, currency_id, source, return_all_on_fail=True)
    for user_id, _ in updates:
        await CacheManager().expire_cache(
            category=CacheCategoryEnum.ACCOUNT, data_id=get_uni_id(user_id, currency_id)
        )


async def batch_add_balance(
    updates: list[tuple[str, float]],
    currency_id: str | None = None,
    source: str = "batch_update",
) -> list[UserAccountData] | None:
    """批量添加账户余额

    Args:
        updates (list[tuple[str, float]]): 元组列表，包含用户id和金额
        currency_id (str | None, optional): 货币ID. Defaults to None.
        source (str, optional): 源说明. Defaults to "batch_update".

    Returns:
        None: None
    """
    if currency_id is None:
        currency_id = DEFAULT_CURRENCY_UUID.hex
    await _batch_add(updates, currency_id, source, return_all_on_fail=True)
    for user_id, _ in updates:
        await CacheManager().expire_cache(
            category=CacheCategoryEnum.ACCOUNT, data_id=get_uni_id(user_id, currency_id)
        )


async def add_balance(
    user_id: str,
    amount: float,
    source: str = "_transfer",
    currency_id: str | None = None,
) -> None:
    """添加用户余额

    Args:
        user_id (str): 用户ID
        amount (float): 金额
        source (str, optional): 源描述. Defaults to "_transfer".
        currency_id (str | None, optional): 货币ID(不填使用默认). Defaults to None.

    Raises:
        RuntimeError: 如果添加失败则抛出异常

    Returns:
        None: None
    """

    if currency_id is None:
        currency_id = DEFAULT_CURRENCY_UUID.hex
    data = await _a_balance(user_id, currency_id, amount, source)
    if not data.success:
        raise RuntimeError(data.message)
    await CacheManager().expire_cache(
        category=CacheCategoryEnum.ACCOUNT, data_id=get_uni_id(user_id, currency_id)
    )


async def del_balance(
    user_id: str,
    amount: float,
    source: str = "_transfer",
    currency_id: str | None = None,
) -> None:
    """减少一个账户的余额

    Args:
        user_id (str): 用户ID
        amount (float): 金额
        source (str, optional): 源说明. Defaults to "_transfer".
        currency_id (str | None, optional): 货币ID(不填则使用默认货币). Defaults to Noen.

    Raises:
        RuntimeError: 如果失败则抛出

    Returns:
        UserAccountData: 用户数据
    """
    if currency_id is None:
        currency_id = DEFAULT_CURRENCY_UUID.hex
    data = await _d_balance(user_id, currency_id, amount, source)
    if not data.success:
        raise RuntimeError(data.message)
    await CacheManager().expire_cache(
        category=CacheCategoryEnum.ACCOUNT, data_id=get_uni_id(user_id, currency_id)
    )


async def transfer_funds(
    from_id: str,
    to_id: str,
    amount: float,
    source: str = "",
    currency_id: str | None = None,
) -> None:
    """转账

    Args:
        from_id (str): 源账户
        to_id (str): 目标账户
        amount (float): 金额
        source (str, optional): 来源说明. Defaults to "from {from_id} to {to_id}".
        currency_id (str | None, optional): 货币ID（不填则使用默认货币）. Defaults to None.

    Raises:
        RuntimeError: 失败则抛出

    Returns:
        None: None
    """
    if currency_id is None:
        currency_id = DEFAULT_CURRENCY_UUID.hex
    if not source:
        source = f"from '{from_id}' to '{to_id}'"
    data = await _transfer(from_id, to_id, currency_id, amount, source)
    if not data.success:
        raise RuntimeError(data.message)
