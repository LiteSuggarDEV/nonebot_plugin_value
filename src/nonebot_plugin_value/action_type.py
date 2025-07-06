class Method:
    """交易记录方法"""

    __DEPOSIT = "DEPOSIT"  # 存款
    __WITHDRAW = "WITHDRAW"  # 取款
    __TRANSFER_IN = "TRANSFER_IN"  # 转入（与转出同时存在）
    __TRANSFER_OUT = "TRANSFER_OUT"  # 转出（与转入同时存在）

    @classmethod
    def deposit(cls) -> str:
        return cls.__DEPOSIT

    @classmethod
    def withdraw(cls) -> str:
        return cls.__WITHDRAW

    @classmethod
    def transfer_in(cls) -> str:
        return cls.__TRANSFER_IN

    @classmethod
    def transfer_out(cls) -> str:
        return cls.__TRANSFER_OUT

    @classmethod
    def valid_actions(cls, action: str) -> bool:
        return action in cls.__dict__.values()
