# nonebot_plugin_value 通用经济系统插件-API 文档

## 数据模型关系图

```mermaid
erDiagram
    currency_meta ||--o{ user_accounts : "1:n"
    currency_meta ||--o{ transactions : "1:n"
    user_accounts ||--o{ transactions : "1:n"

    currency_meta {
        string id PK "UUID主键"
        string display_name "显示名称"
        string symbol "货币符号"
        float default_balance "默认余额"
        boolean allow_negative "允许负余额"
        datetime created_at "创建时间"
    }

    user_accounts {
        string uni_id PK "用户唯一标识(由id和currency_id组合形成)"
        string id PK "用户ID"
        string currency_id FK "货币ID (与id组成唯一约束)"
        float balance "账户余额"
        datetime last_updated "最后更新时间"
    }

    transactions {
        string id PK "交易ID"
        string account_id FK "账户ID (索引)"
        string currency_id FK "货币ID"
        float amount "交易金额"
        string action "交易类型"
        string source "交易来源"
        float balance_before "交易前余额"
        float balance_after "交易后余额"
        datetime timestamp "交易时间 (索引)"
    }
```

## API 文档

> 文档内,`~`表示**nonebot_plugin_value**模块

---

> 开发规范：我们推荐您使用 UUID.hex 作为唯一 ID，而不是直接传入 ID。

### [标准 API(表现层)](./apis/standard.md)

### [进阶 API(服务层)](./apis/advanced.md)

### [底层 API(数据层)](./apis/kernel.md)
