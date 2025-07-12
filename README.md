<div align="center">
  <a href="https://github.com/JohnRichard4096/nonebot_plugin_value/">
    <img src="https://github.com/user-attachments/assets/b5162036-5b17-4cf4-b0cb-8ec842a71bc6" width="200" alt="value Logo">
  </a>
  <h1>Value</h1>
  <h3>基于SQLAlchemy长期存储的新一代经济API</h3>

  <p>
    <a href="https://pypi.org/project/nonebot-plugin-value/">
      <img src="https://img.shields.io/pypi/v/nonebot-plugin-value?color=blue&style=flat-square" alt="PyPI Version">
    </a>
    <a href="https://www.python.org/">
      <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&style=flat-square" alt="Python Version">
    </a>
    <a href="https://nonebot.dev/">
      <img src="https://img.shields.io/badge/nonebot2-2.4.0+-blue?style=flat-square" alt="NoneBot Version">
    </a>
    <a href="LICENSE">
      <img src="https://img.shields.io/github/license/JohnRichard4096/nonebot_plugin_value?style=flat-square" alt="License">
    </a>
    <a href="https://qm.qq.com/q/PFcfb4296m">
      <img src="https://img.shields.io/badge/QQ%E7%BE%A4-1002495699-blue?style=flat-square" alt="QQ Group">
    </a>
  </p>
</div>

## 核心特性

`nonebot_plugin_value` 是一个基于 NoneBot2 的通用经济系统插件，提供以下核心功能：

- 📈 账户系统：各货币账户独立
- 🪙 多货币系统：支持创建任意数量的货币类型
- 💰 原子化交易：保证转账等操作的事务性
- 🔁 钩子系统：支持交易前后触发自定义逻辑
- 📊 完整审计：所有交易记录包含完整上下文信息
- 🔐 安全控制：支持负余额限制

### 快速开始

#### 安装

- 使用 uv 安装:

  ```bash
  uv add nonebot-plugin-value
  ```

- 使用 pip 安装:

  ```bash
  pip install nonebot-plugin-value
  ```

#### 加载插件

打开`pyproject.toml`

```toml
[tool.nonebot]
plugins = ["nonebot_plugin_value"]
```

添加依赖后，请重新启动 nonebot2

### [API Docs](docs/api.md)

### 更新迁移

1. 升级 nonebot_plugin_value 到最新版本

2. 运行迁移脚本(（如果 Bot 根目录下**没有**迁移脚本目录，请使用`nb orm init`来初始化。）在 bot 根目录使用`nb orm revison`再`nb orm upgrade`进行迁移)
