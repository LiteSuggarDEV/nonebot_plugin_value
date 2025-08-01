from typing import Any


class BaseException(Exception):
    """
    Base exception class for this module.
    """

    def __init__(self, message: str = "", data: Any | None = None):
        self.message = message
        self.data = data


class CancelAction(BaseException):
    """
    Exception raised when the user cancels an action.
    """


class DataUpdate(Exception):
    """
    Exception raised when the data updated
    """

    def __init__(self, amount: float) -> None:
        self.amount = amount
