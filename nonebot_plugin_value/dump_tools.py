import json
from pathlib import Path

import aiofiles
from nonebot import logger
from nonebot_plugin_orm import get_session
from pydantic import BaseModel, Field

from .api.api_balance import list_accounts
from .api.api_currency import list_currencies, update_currency
from .api.api_transaction import get_transaction_history
from .pyd_models.balance_pyd import UserAccountData
from .pyd_models.currency_pyd import CurrencyData
from .pyd_models.transaction_pyd import TransactionData
from .repository import (
    AccountRepository,
    TransactionRepository,
)


class AccountMigrationData(BaseModel):
    account_data: UserAccountData = Field(default_factory=UserAccountData)
    transactions: list[TransactionData] = []


class MigrationData(BaseModel):
    currencies: list[CurrencyData] = []
    accounts: list[AccountMigrationData] = []


async def dump_data() -> MigrationData:
    """导出数据

    Returns:
        MigrationData: 导出的数据模型
    """
    logger.info("Dumping data...")
    data = MigrationData()
    currencies = await list_currencies()
    data.currencies = currencies
    for currency in currencies:
        accounts = await list_accounts(currency_id=currency.id)
        for account in accounts:
            transactions = await get_transaction_history(account.id, 100)
            data.accounts.append(
                AccountMigrationData(
                    account_data=account,
                    transactions=transactions,
                )
            )

    return data


async def dump_data_to_json_file(dir: Path):
    """导出到文件

    Args:
        dir (Path): 目录
    """
    data = await dump_data()
    logger.info(f"Writing migration data to {(dir / 'migration.json')!s}")
    async with aiofiles.open(str(dir / "migration.json"), "w", encoding="utf-8") as f:
        await f.write(data.model_dump_json(indent=4))


async def migrate_from_data(data: MigrationData) -> None:
    """从迁移数据更新数据库数据

    Args:
        data (MigrationData): 迁移数据
    """
    logger.info("Migrating from data")
    for currency in data.currencies:
        logger.info(f"Updating currency {currency.id}")
        await update_currency(currency)
    async with get_session() as session:
        account_repo = AccountRepository(session)
        tx_repo = TransactionRepository(session)
        for account in data.accounts:
            logger.info(f"Updating account {account.account_data.id}")
            await account_repo.get_or_create_account(
                account.account_data.id, account.account_data.currency_id
            )
            await account_repo.update_balance(
                account.account_data.id,
                account.account_data.balance,
                account.account_data.currency_id,
            )
            for transaction in account.transactions:
                await tx_repo.create_transaction(
                    account.account_data.id,
                    transaction.currency_id,
                    transaction.amount,
                    transaction.action,
                    transaction.source,
                    transaction.balance_before,
                    transaction.balance_after,
                    transaction.timestamp,
                )


async def migrate_from_json_file(path: Path):
    """从JSON迁移数据

    Args:
        path (Path): JSON文件路径
    """
    logger.info("Loading data from JSON file...")
    async with aiofiles.open(path) as f:
        data = MigrationData.model_validate(json.loads(await f.read()))
    await migrate_from_data(data)
