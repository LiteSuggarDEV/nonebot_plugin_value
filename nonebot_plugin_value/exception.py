class BaseFailed(Exception):
    """
    Base failed exception for all exceptions
    """


# start of basic exceptions


class AccountException(BaseFailed):
    """
    Account exception
    """


class CurrencyException(BaseFailed):
    """
    Currency exception
    """


class TransactionException(BaseFailed):
    """
    Transaction exception
    """


# end of basic exceptions


# start of not found exceptions


class NotFoundException(BaseFailed):
    """
    Not found exception
    """


class AccountNotFound(NotFoundException, AccountException):
    """
    Account not found exception
    """


class CurrencyNotFound(NotFoundException, CurrencyException):
    """
    Currency not found exception
    """


class TransactionNotFound(NotFoundException, TransactionException):
    """
    Transaction not found exception
    """


# end of not found exceptions

# start of other exceptions


class AccountFrozen(AccountException):
    """
    Account frozen exception (will be raised when trying to perform an action on a frozen account)
    """
