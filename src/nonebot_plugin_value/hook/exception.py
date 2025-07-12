class BaseException(Exception):
    """
    Base exception class for this module.
    """

    def __init__(self, message: str = ""):
        self.message = message


class CancelAction(BaseException):
    """
    Exception raised when the user cancels an action.
    """
