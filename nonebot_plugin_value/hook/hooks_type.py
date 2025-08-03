from enum import Enum


class HooksType(Enum, str):
    PRE = "vault_pre_transaction"
    POST = "vault_post_transaction"

    @classmethod
    def pre(cls) -> str:
        return cls.PRE

    @classmethod
    def post(cls) -> str:
        return cls.POST
    @classmethod
    def methods(cls) -> list[str]:
        return [hook.value for hook in cls]
