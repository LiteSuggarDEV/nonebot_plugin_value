class HooksType:
    __pre = "vault_pre_transaction"
    __post = "vault_post_transaction"

    @classmethod
    def pre(cls) -> str:
        return cls.__pre

    @classmethod
    def post(cls) -> str:
        return cls.__post

    @classmethod
    def valid_hooks(cls, hook_name: str) -> bool:
        return hook_name in [cls.__pre, cls.__post]

    @classmethod
    def methods(cls) -> list[str]:
        return [cls.__pre, cls.__post]
