import sys
from pathlib import Path

import nonebot
import pytest
from pytest_asyncio import is_async_test

# 将项目根目录添加到sys.path中
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def pytest_collection_modifyitems(items: list[pytest.Item]):
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


@pytest.fixture(scope="session", autouse=True)
async def after_nonebot_init(after_nonebot_init: None):
    # 加载插件
    nonebot.load_from_toml("pyproject.toml")
