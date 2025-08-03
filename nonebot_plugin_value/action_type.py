from enum import Enum


class Method(str, Enum):
    """交易记录方法"""

    DEPOSIT = "DEPOSIT"  # 存款
    WITHDRAW = "WITHDRAW"  # 取款
    TRANSFER_IN = "TRANSFER_IN"  # 转入（与转出同时存在）
    TRANSFER_OUT = "TRANSFER_OUT"  # 转出（与转入同时存在）
