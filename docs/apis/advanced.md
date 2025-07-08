# Value-进阶API文档

> **本API为服务层API，包含核心逻辑**

## currency-API(`~~`代指`~.db_api.balance`)

<details>

### `~~.list_currencies`

```python
async def list_currencies(session: AsyncSession | None = None):
    """获取已存在的货币

    Args:
        session (AsyncSession | None, optional): 异步Session

    Returns:
        Sequence[CurrencyMeta]: 返回货币列表
    """
    ...
```

### `~~.getcurrency`

```python
async def getcurrency(
    currency_id: str, session: AsyncSession | None = None
) -> CurrencyMeta | None:
    """获取一个货币的元信息

    Args:
        session (AsyncSession | None, optional): SQLAlchemy的异步session
        currency_id (str): 货币唯一ID

    Returns:
        CurrencyMeta | None: 货币元数据（不存在为None）
    """
    ...
```

### `~~.get_or_create_currency`

```python
async def get_or_create_currency(
    currency_data: CurrencyData,
    session: AsyncSession | None = None,
) -> tuple[CurrencyMeta, bool]:
    """获取或创建新货币（如果存在就获取）

    Args:
        session (AsyncSession | None, optional): SQLAlchemy的异步session
        currency_data (CurrencyData): 货币元信息

    Returns:
        tuple[CurrencyMeta, bool] 元数据和是否创建
    """
    ...
```

### `~~.get_default_currency`

```python
async def get_default_currency(session: AsyncSession|None=None) -> CurrencyMeta:
    """获取默认货币

    Args:
        session (AsyncSession | None, optional): 异步会话. Defaults to None.

    Returns:
        CurrencyMeta: 货币元数据
    """
    ...
```


</details>

---

## balance-API(`~~`代指`~.db_api.balance`)

<details>

### `~~.get_or_create_account`

```python
async def get_or_create_account(
    user_id: str,
    currency_id: str,
    session: AsyncSession | None = None,
) -> UserAccount:
    """获取或创建一个货币的账户

    Args:
        user_id (str): 用户ID
        currency_id (str): 货币ID
        session (AsyncSession | None, optional): 异步会话. Defaults to None.

    Returns:
        UserAccount: 用户数据模型
    """
    ...
```

### `~~.del_balance`

```python
async def del_balance(
    user_id: str,
    currency_id: str,
    amount: float,
    source: str = "",
    session: AsyncSession | None = None,
) -> dict[str, Any]:
    """异步减少余额

    Args:
        user_id (str): 用户ID
        currency_id (str): 货币ID
        amount (float): 数量
        source (str, optional): 来源说明. Defaults to "".
        session (AsyncSession | None, optional): 数据库异步会话. Defaults to None.

    Returns:
        dict[str, Any]: 包含是否成功的说明
    """
    ...
```

### `~~.add_balance`

```python
async def add_balance(
    user_id: str,
    currency_id: str,
    amount: float,
    source: str = "",
    session: AsyncSession | None = None,
) -> dict[str, Any]:
    """异步增加余额

    Args:
        user_id (str): 用户ID
        currency_id (str): 货币ID
        amount (float): 数量
        source (str, optional): 来源说明. Defaults to "".
        session (AsyncSession | None, optional): 数据库异步会话. Defaults to None.

    Returns:
        dict[str, Any]: 是否成功("success")，消息说明("message")
    """
    ...
```

### `~~.transfer_funds`

```python
async def transfer_funds(
    fromuser_id: str,
    touser_id: str,
    currency_id: str,
    amount: float,
    source: str = "transfer",
    session: AsyncSession | None = None,
) -> dict[str, Any]:
    """异步转账

    Args:
        fromuser_id (str): 源用户ID
        touser_id (str): 目标用户ID
        currency_id (str): 货币ID
        amount (float): 数量
        source (str, optional): 源说明. Defaults to "transfer".
        session (AsyncSession | None, optional): 数据库异步Session. Defaults to None.

    Returns:
        dict[str, Any]: 如果成功则包含"from_balance"（源账户现在的balance），"to_balance"（目标账户现在的balance），否则包含"message"（错误消息）字段
    """
    ...
```


</details>

---

## transaction-API(`~~`代指`~.db_api.transaction`)

<details>

### `~~.get_transaction_history`

```python
async def get_transaction_history(
    account_id: str,
    limit: int = 100,
    session: AsyncSession | None = None,
):
    """获取一个用户的交易记录

    Args:
        session (AsyncSession | None, optional): 异步数据库会话
        account_id (str): 用户UUID(应自行处理)
        limit (int, optional): 数据条数. Defaults to 100.

    Returns:
        Sequence[Transaction]: 记录列表
    """
    ...
```

</details>
