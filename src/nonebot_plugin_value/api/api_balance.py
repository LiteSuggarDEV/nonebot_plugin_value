from nonebot_plugin_orm import get_session

from ..pyd_models.balance_pyd import UserAccountData
from ..services.balance import add_balance as _a_balance
from ..services.balance import del_account as _del_account
from ..services.balance import del_balance as _d_balance
from ..services.balance import get_or_create_account as _go_account
from ..services.balance import list_accounts as _list_accounts
from ..services.balance import transfer_funds as _transfer
from .api_currency import get_default_currency as _get_default


async def list_accounts(currency_id: str | None = None) -> list[UserAccountData]:
    """获取指定货币（或默认）的账户列表

    Args:
        currency_id (str | None, optional): 货币ID. Defaults to None.

    Returns:
        list[UserAccountData]: 包含用户数据的列表
    """
    if currency_id is None:
        currency_id = (await _get_default()).id
    async with get_session() as session:
        return [
            UserAccountData(
                id=account.id,
                uni_id=account.uni_id,
                currency_id=account.currency_id,
                balance=account.balance,
                last_updated=account.last_updated,
            )
            for account in await _list_accounts(session, currency_id)
        ]


async def del_account(user_id: str, currency_id: str | None = None) -> bool:
    """删除账户

    Args:
        user_id (str): 用户ID
        currency_id (str | None, optional): 货币ID(不填则使用默认货币). Defaults to None.

    Returns:
        bool: 是否成功
    """
    if currency_id is None:
        currency_id = (await _get_default()).id
    return await _del_account(user_id)


async def get_or_create_account(
    user_id: str, currency_id: str | None = None
) -> UserAccountData:
    """获取账户数据（不存在就创建）

    Args:
        user_id (str): 用户ID
        currency_id (str | None, optional): 货币ID(不填则使用默认货币)

    Returns:
        UserAccountData: 用户数据
    """
    if currency_id is None:
        currency_id = (await _get_default()).id
    async with get_session() as session:
        data = await _go_account(user_id, currency_id, session)
        return UserAccountData(
            id=data.id,
            uni_id=data.uni_id,
            currency_id=data.currency_id,
            balance=data.balance,
            last_updated=data.last_updated,
        )


async def add_balance(
    user_id: str,
    amount: float,
    source: str = "_transfer",
    currency_id: str | None = None,
) -> UserAccountData:
    """添加用户余额

    Args:
        user_id (str): 用户ID
        amount (float): 金额
        source (str, optional): 源描述. Defaults to "_transfer".
        currency_id (str | None, optional): 货币ID(不填使用默认). Defaults to None.

    Raises:
        RuntimeError: 如果添加失败则抛出异常

    Returns:
        UserAccountData: 用户账户数据
    """

    if currency_id is None:
        currency_id = (await _get_default()).id
    data = await _a_balance(user_id, currency_id, amount, source)
    if not data.success:
        raise RuntimeError(data.message)
    return await get_or_create_account(user_id, currency_id)


async def del_balance(
    user_id: str,
    amount: float,
    source: str = "_transfer",
    currency_id: str | None = None,
) -> UserAccountData:
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
        currency_id = (await _get_default()).id
    data = await _d_balance(user_id, currency_id, amount, source)
    if not data.success:
        raise RuntimeError(data.message)
    return await get_or_create_account(user_id, currency_id)


async def transfer_funds(
    from_id: str,
    to_id: str,
    amount: float,
    source: str = "",
    currency_id: str | None = None,
) -> UserAccountData:
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
        UserAccountData: 用户账户数据
    """
    if currency_id is None:
        currency_id = (await _get_default()).id
    if not source:
        source = f"from '{from_id}' to '{to_id}'"
    data = await _transfer(from_id, to_id, currency_id, amount, source)
    if not data.success:
        raise RuntimeError(data.message)
    return await get_or_create_account(to_id, currency_id)
