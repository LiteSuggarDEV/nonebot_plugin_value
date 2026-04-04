rm data.sqlite3
nb orm upgrade
uv run pytest tests/* --cov=nonebot_plugin_value --cov-report=term-missing --cov-report=xml --junitxml=test-results.xml -v
