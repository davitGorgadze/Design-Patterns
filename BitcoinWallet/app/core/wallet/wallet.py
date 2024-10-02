from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Protocol, Tuple


class IWallet(Protocol):
    def get_user(self) -> int:
        pass

    def deposit(self, amount: float) -> None:
        pass

    def withdraw(self, amount: float) -> None:
        pass

    def get_address(self) -> int:
        pass

    def get_amount(self) -> float:
        pass

    def set_address(self, wallet_address: int) -> None:
        pass


class IWalletRepository(Protocol):
    def create_wallet(self, api_key: str) -> Tuple[Optional[IWallet], Optional[str]]:
        pass

    def get_wallet(
        self, api_key: str, address: int
    ) -> Tuple[Optional[IWallet], Optional[str]]:
        pass

    def num_wallets(self, user_id: int) -> int:
        pass

    def deposit(self, wallet_address: int, amount: float) -> Tuple[bool, Optional[str]]:
        pass

    def withdraw(
        self, wallet_address: int, amount: float
    ) -> Tuple[bool, Optional[str]]:
        pass

    def wallets_belong_to_the_same_user(
        self, first_wallet_address: int, second_wallet_address: int
    ) -> bool:
        pass

    def get_user_wallets(self, user_id: int) -> List[IWallet]:
        pass

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass

    @abstractmethod
    def default_wallet(self, uid: int) -> IWallet:
        pass


@dataclass
class BitcoinWallet:
    wallet_address: int
    user_id: int
    amount_BTC: float

    def get_user(self) -> int:
        return self.user_id

    def deposit(self, amount: float) -> None:
        self.amount_BTC += amount

    def withdraw(self, amount: float) -> None:
        self.amount_BTC -= amount

    def get_address(self) -> int:
        return self.wallet_address

    def get_amount(self) -> float:
        return self.amount_BTC

    def set_address(self, wallet_address: int) -> None:
        self.wallet_address = wallet_address
