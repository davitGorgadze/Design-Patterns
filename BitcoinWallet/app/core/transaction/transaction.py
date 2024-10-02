from dataclasses import dataclass
from typing import List, Protocol

from app.utils.result import Result


class ITransaction(Protocol):
    def calculate_system_profit(self) -> float:
        pass

    def get_balance(self) -> float:
        pass

    def get_sender_address(self) -> int:
        pass

    def get_receiver_address(self) -> int:
        pass


@dataclass
class SimpleTransaction:
    sender_address: int
    receiver_address: int
    balance: float
    transaction_id: int = 0

    def calculate_system_profit(self) -> float:
        return 0

    def get_balance(self) -> float:
        return self.balance

    def get_sender_address(self) -> int:
        return self.sender_address

    def get_receiver_address(self) -> int:
        return self.receiver_address


@dataclass
class BaseTransactionDecorator:
    inner: ITransaction

    def calculate_system_profit(self) -> float:
        return self.inner.calculate_system_profit()

    def get_balance(self) -> float:
        return self.inner.get_balance()

    def get_sender_address(self) -> int:
        return self.inner.get_sender_address()

    def get_receiver_address(self) -> int:
        return self.inner.get_receiver_address()


@dataclass
class TransactionBetweenUsers(BaseTransactionDecorator):
    def calculate_system_profit(self) -> float:
        return self.inner.get_balance() * 0.15


class ITransactionRepository(Protocol):
    def create(self, transaction: ITransaction) -> Result[int]:
        pass

    def get_wallet_transactions(
        self, wallet_address: int
    ) -> Result[List[ITransaction]]:
        pass

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass

    def get_transaction_count(self) -> Result[int]:
        pass
