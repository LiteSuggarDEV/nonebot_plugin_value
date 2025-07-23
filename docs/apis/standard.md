# EconomyValue-标准 API 文档

> **标准 API 文档**

## balance-API(`~~`代指`~.api.api_balance`)

<details>

### `~~.list_accounts`

```python
async def list_accounts(currency_id: str | None = None) -> list[UserAccountData]:
    """获取指定货币（或默认）的账户列表

    Args:
        currency_id (str | None, optional): 货币ID. Defaults to None.

    Returns:
        list[UserAccountData]: 包含用户数据的列表
    """
    ...
```

### `~~.get_or_create_account`

```python
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
    ...
```

### `~.del_account`

```python
async def del_account(user_id: str, currency_id: str | None = None) -> bool:
    """删除账户

    Args:
        user_id (str): 用户ID
        currency_id (str | None, optional): 货币ID(不填则使用默认货币). Defaults to None.

    Returns:
        bool: 是否成功
    """
```

### `~~.add_balance`

```python
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
    ...
```

### `batch_add_balance`

```python
async def batch_add_balance(
    updates: list[tuple[str, float]],
    currency_id: str | None = None,
    source: str = "batch_update",
) -> list[UserAccountData]:
    """批量添加账户余额

    Args:
        updates (list[tuple[str, float]]): 元组列表，包含用户id和金额
        currency_id (str | None, optional): 货币ID. Defaults to None.
        source (str, optional): 源说明. Defaults to "batch_update".

    Returns:
        list[UserAccountData]: 用户账户数据列表
    """
    ...
```

### `~~.del_balacne`

```python
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
    ...
```

### `~~.batch_del_balance`

```python
async def batch_del_balance(
    updates: list[tuple[str, float]],
    currency_id: str | None = None,
    source: str = "batch_update",
) -> list[UserAccountData]:
    """批量减少账户余额

    Args:
        updates (list[tuple[str, float]]): 元组列表，包含用户id和金额
        currency_id (str | None, optional): 货币ID. Defaults to None.
        source (str, optional): 源说明. Defaults to "batch_update".

    Returns:
        list[UserAccountData]: 用户账户数据列表
    """
    ...
```

### `~~.transfer_funds`

```python
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
    ...
```

</details>

---

## currency-API(`~~`代指`~.api.api_currency`)

<details>

### `~~.get_or_create_currency`

```python
async def get_or_create_currency(currency_data: CurrencyData) -> CurrencyData:
    """获取或者创建货币

    Args:
        currency_data (CurrencyData): 货币数据

    Returns:
        CurrencyData: 货币数据
    """
    ...
```

### `~~.update_currency`

```python
async def update_currency(currency_data: CurrencyData) -> CurrencyData:
    """更新货币信息

    Args:
        currency_data (CurrencyData): 货币数据

    Returns:
        CurrencyData: 货币数据
    """
    ...
```

### `~~.list_currencies`

```python
async def list_currencies() -> list[CurrencyData]:
    """获取所有已存在货币

    Returns:
        list[CurrencyData]: 包含所有已存在货币的列表
    """
    ...
```

### `~~.get_currency`

```python
async def get_currency(currency_id: str) -> CurrencyData | None:
    """获取一个货币信息

    Args:
        currency_id (str): 货币唯一ID

    Returns:
        CurrencyData | None: 货币数据，如果不存在则返回None
    """
    ...
```

### `~~.get_default_currency`

```python
async def get_default_currency() -> CurrencyData:
    """获取默认货币的信息

    Returns:
        CurrencyData: 货币信息
    """
    ...
```

### `~~.create_currency`

```python
async def create_currency(currency_data: CurrencyData) -> CurrencyData:
    """创建货币

    Args:
        currency_data (CurrencyData): 货币数据

    Returns:
        CurrencyData: 货币数据
    """
    ...
```

### `~~.remove_currency`

```python
async def remove_currency(currency_id: str):
    """删除一个货币（警告！这是一个及其危险的操作！这会删除所有关联的账户！）

    Args:
        currency_id (str): 货币唯一ID

    Returns:
        bool: 是否删除成功
    """
    ...
```

</details>

## transaction-API(`~~`代指`~.api.api_transaction`)

<details>

### `~~.get_transaction_history_by_time_range`

```python
async def get_transaction_history_by_time_range(
    account_id: str,
    start_time: float,
    end_time: float,
    limit: int = 10,
) -> list[TransactionData]:
    """通过时间范围获取交易记录

    Args:
        account_id (str): 账户ID
        start_time (datetime): 开始时间
        end_time (datetime): 结束时间
        limit (int, optional): 最大记录数. Defaults to 10.

    Returns:
        list[TransactionData]: 交易记录
    """
    ...
```

### `~~.get_transaction_history`

```python
async def get_transaction_history(
    account_id: str,
    limit: int = 10,
) -> list[TransactionData]:
    """获取账户历史交易记录

    Args:
        account_id (str): 账户ID
        limit (int, optional): 数量. Defaults to 10.

    Returns:
        list[TransactionData]: 包含交易数据的列表
    """
    ...
```

### `~~.remove_transaction`

```python
async def remove_transaction(transaction_id: str) -> bool:
    """删除交易记录

    Args:
        transaction_id (str): 交易ID

    Returns:
        bool: 是否成功删除
    """
    ...
```

</details>
