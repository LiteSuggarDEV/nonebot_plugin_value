from uuid import UUID, uuid5

# UUID namespace常量定义。
NAMESPACE_VALUE = UUID("e6fec076-98df-4979-8618-36ad04dea39f")


def to_uuid(s: str) -> str:
    return uuid5(NAMESPACE_VALUE, s).hex
