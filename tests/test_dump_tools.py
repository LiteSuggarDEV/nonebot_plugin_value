import json
import tempfile
from pathlib import Path

import aiofiles
import pytest
from nonebug import App  # type:ignore


@pytest.mark.asyncio
async def test_dump_and_migrate(app: App):
    """测试数据导出和导入功能"""
    from nonebot_plugin_value.api.api_balance import (
        add_balance,
        get_or_create_account,
    )
    from nonebot_plugin_value.api.api_currency import (
        CurrencyData,
        get_or_create_currency,
    )
    from nonebot_plugin_value.dump_tools import (
        dump_data,
        dump_data_to_json_file,
        migrate_from_data,
        migrate_from_json_file,
    )
    from nonebot_plugin_value.uuid_lib import to_uuid

    # 创建测试数据
    test_currency_id = to_uuid("test_currency")
    test_user_id = to_uuid("test_user")

    # 创建货币
    currency_data = CurrencyData(
        id=test_currency_id, display_name="Test Currency", symbol="TC"
    )
    await get_or_create_currency(currency_data)

    # 创建账户并添加余额
    await get_or_create_account(test_user_id, test_currency_id)
    await add_balance(test_user_id, 100.0, "test_add", test_currency_id)

    # 验证初始状态
    account_before = await get_or_create_account(test_user_id, test_currency_id)
    assert account_before.balance == 100.0

    # 测试导出功能
    exported_data = await dump_data()
    assert len(exported_data.currencies) >= 1, "应该至少有一个货币"
    assert len(exported_data.accounts) >= 1, "应该至少有一个账户"

    # 验证导出的数据包含我们的测试数据
    exported_currency_ids = [c.id for c in exported_data.currencies]
    assert test_currency_id in exported_currency_ids, "导出的货币应该包含测试货币"

    exported_account_ids = [a.account_data.id for a in exported_data.accounts]
    assert test_user_id in exported_account_ids, "导出的账户应该包含测试账户"

    # 测试导出到 JSON 文件
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        await dump_data_to_json_file(tmp_path)

        # 验证文件存在
        json_file = tmp_path / "migration.json"
        assert json_file.exists(), "JSON 文件应该被创建"

        # 验证文件内容（使用异步方式读取）
        async with aiofiles.open(json_file, encoding="utf-8") as f:
            file_content = await f.read()
            file_data = json.loads(file_content)
            assert "currencies" in file_data, "JSON 应该包含 currencies 字段"
            assert "accounts" in file_data, "JSON 应该包含 accounts 字段"

    # 测试从数据模型迁移（修改余额）
    await add_balance(test_user_id, 50.0, "test_add2", test_currency_id)
    account_after_add = await get_or_create_account(test_user_id, test_currency_id)
    assert account_after_add.balance == 150.0, "充值后余额应为 150.0"

    # 重新导出当前状态
    current_data = await dump_data()

    # 修改导出数据中的余额
    for account in current_data.accounts:
        if account.account_data.id == test_user_id:
            account.account_data.balance = 200.0
            for tx in account.transactions:
                if tx.amount == 50.0:
                    tx.amount = 100.0  # 修改交易记录

    # 执行迁移
    await migrate_from_data(current_data)

    # 验证迁移后的余额
    account_after_migrate = await get_or_create_account(test_user_id, test_currency_id)
    assert account_after_migrate.balance == 200.0, "迁移后余额应为 200.0"

    # 测试从 JSON 文件迁移
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        json_file = tmp_path / "migration.json"

        # 创建新的测试数据
        test_user2_id = to_uuid("test_user2")
        await get_or_create_account(test_user2_id, test_currency_id)
        await add_balance(test_user2_id, 75.0, "test_user2_add", test_currency_id)

        # 导出并修改
        data_to_export = await dump_data()
        async with aiofiles.open(json_file, "w", encoding="utf-8") as f:
            await f.write(data_to_export.model_dump_json(indent=4))

        # 修改余额为 300
        for account in data_to_export.accounts:
            if account.account_data.id == test_user2_id:
                account.account_data.balance = 300.0

        # 写入修改后的数据
        async with aiofiles.open(json_file, "w", encoding="utf-8") as f:
            await f.write(data_to_export.model_dump_json(indent=4))

        # 从文件迁移
        await migrate_from_json_file(json_file)

        # 验证迁移结果
        account_after_file_migrate = await get_or_create_account(
            test_user2_id, test_currency_id
        )
        assert account_after_file_migrate.balance == 300.0, "从文件迁移后余额应为 300.0"
