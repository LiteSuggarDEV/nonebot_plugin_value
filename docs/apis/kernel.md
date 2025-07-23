# EconomyValue-底层 API 文档

> **本 API 为数据层 API，包含操作数据库的底层逻辑**

## Repository(`~.repository`)

### 变量定义：

```python
DEFAULT_NAME = "DEFAULT_CURRENCY_USD"
DEFAULT_CURRENCY_UUID = uuid5(NAMESPACE_VALUE, "nonebot_plugin_value")
```

---

### CurrencyRepository(`~.repository.CurrencyRepository`)

<details>

```python
class CurrencyRepository:
    """货币元数据操作"""

    def __init__(self, session: AsyncSession):
        ...

    async def get_or_create_currency(
        self, currency_data: CurrencyData
    ) -> tuple[CurrencyMeta, bool]:
        """获取或创建货币"""

    async def createcurrency(self, currency_data: CurrencyData) -> None:
        """创建新货币"""
        ...

    async def update_currency(self, currency_data: CurrencyData) -> CurrencyMeta:
        """更新货币信息"""

    async def get_currency(self, currency_id: str) -> CurrencyMeta | None:
        """获取货币信息"""
        ...

    async def remove_currency(self, currency_id: str):
        """删除货币（警告！会同时删除所有关联账户！）"""
        ...
```

</details>

---

### AccountRepository(`~.repository.AccountRepository`)

<details>

```python
class AccountRepository:
    """账户操作"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_account(
        self, user_id: str, currency_id: str
    ) -> UserAccount:
        """获取或创建用户账户"""
        ...

    async def get_balance(self, account_id: str) -> float | None:
        """获取账户余额"""
        ...

    async def update_balance(
        self, account_id: str, amount: float, currency_id: str
    ) -> tuple[float, float]:
        """更新余额"""
        ...

    async def list_accounts(self, currency_id: str | None = None):
        """列出所有账户"""
        ...

    async def remove_account(self, account_id: str):
        """删除账户"""
        ...
```

</details>

---

### TransactionRepository(`~.repository.TransactionRepository`)

<details>

```python
class TransactionRepository:
    """交易操作"""

    def __init__(self, session: AsyncSession):
        ...

    async def create_transaction(
        self,
        account_id: str,
        currency_id: str,
        amount: float,
        action: str,
        source: str,
        balance_before: float,
        balance_after: float,
        timestamp: datetime | None = None,
    ) -> Transaction:
        """创建交易记录"""
        ...

    async def get_transaction_history(self, account_id: str, limit: int = 100):
        """获取账户交易历史"""
        ...

    async def remove_transaction(self, transaction_id: str) -> bool:
        """删除交易记录"""
        ...
    
    async def get_transaction_history_by_time_range(
        self,
        account_id: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 100,
    ) -> Sequence[Transaction]:
        """获取账户交易历史"""
        ...
```

</details>
