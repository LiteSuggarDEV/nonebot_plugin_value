# EconomyValue 迁移工具文档

## 迁移工具使用方法(nonebot_plugin_value.dump_tools)

```python
async def dump_data() -> MigrationData:
    """导出数据

    Returns:
        MigrationData: 导出的数据模型
    """
    ...


async def dump_data_to_json_file(dir: Path):
    """导出到文件

    Args:
        dir (Path): 目录
    """
    ...


async def migrate_from_data(data: MigrationData) -> None:
    """从迁移数据更新数据库数据

    Args:
        data (MigrationData): 迁移数据
    """
    ...

async def migrate_from_json_file(path: Path):
    """从JSON迁移数据

    Args:
        path (Path): JSON文件路径
    """
    ...
```
