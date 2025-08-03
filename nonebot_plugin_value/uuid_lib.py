from uuid import UUID, uuid5

# UUID namespace常量定义。
NAMESPACE_VALUE = UUID("e6fec076-98df-4979-8618-36ad04dea39f")
DEFAULT_NAME = "DEFAULT_CURRENCY_USD"
DEFAULT_CURRENCY_UUID = uuid5(NAMESPACE_VALUE, DEFAULT_NAME)

def to_uuid(s: str) -> str:
    """获取UUID

    Args:
        s (str): 输入字符串

    Returns:
        str: UUID
    """
    return uuid5(NAMESPACE_VALUE, s).hex


def get_uni_id(user_id: str, currency_id: str) -> str:
    """获取主键unique id

    Args:
        user_id (str): 用户ID
        currency_id (str): 货币ID

    Returns:
        str: unique id
    """
    return uuid5(NAMESPACE_VALUE, f"{user_id}{currency_id}").hex
