from enum import Enum


class HooksType(str, Enum):
    PRE = "vault_pre_transaction"
    POST = "vault_post_transaction"

    @classmethod
    def pre(cls) -> str:
        return cls.PRE.value

    @classmethod
    def post(cls) -> str:
        return cls.POST.value
    @classmethod
    def methods(cls) -> list[str]:
        return [hook.value for hook in cls]
