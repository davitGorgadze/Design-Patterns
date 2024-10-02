from dataclasses import dataclass


@dataclass
class UserNotFoundError(Exception):
    message: str = "INVALID API KEY, USER NOT FOUND"


@dataclass
class WalletNotAccessibleError(Exception):
    message: str = "SENDING WALLET DOES'T BELONG TO AUTHENTICATED USER"


@dataclass
class TransactionError(Exception):
    message: str = "ERROR WHILE MAKING A TRANSACTION. ROLLING BACK"


@dataclass
class WalletRequestError(Exception):
    message: str
