from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from app.core.auth.interactor import IUserRepository
from app.core.wallet.wallet import BitcoinWallet, IWallet


@dataclass
class AbstractInMemoryWalletRepository:
    user_repository: IUserRepository
    max_number_of_wallets: int = field(default=3)
    wallet_dict: Dict[int, List[IWallet]] = field(default_factory=dict)

    def create_wallet(self, api_key: str) -> Tuple[Optional[IWallet], Optional[str]]:
        uid = self.user_repository.get_user_id(api_key)
        if uid is None:
            return None, "Couldn't find wallet with that address"

        if self.num_wallets(user_id=uid) >= self.max_number_of_wallets:
            return None, f"Can't create more than {self.max_number_of_wallets} wallets"

        new_wallet = self.default_wallet(uid)
        if uid in self.wallet_dict:
            self.wallet_dict[uid].append(new_wallet)
        else:
            self.wallet_dict[uid] = [new_wallet]
        return new_wallet, None

    def get_wallet(
        self, api_key: str, address: int
    ) -> Tuple[Optional[IWallet], Optional[str]]:
        uid = self.user_repository.get_user_id(api_key)

        if uid is None:
            return None, "Couldn't verify user"
        if uid not in self.wallet_dict:
            return None, "Couldn't find wallet with that address"

        for wallet in self.wallet_dict[uid]:
            if wallet.get_address() == address:
                return wallet, None

        return None, "Couldn't find wallet with that address"

    def num_wallets(self, user_id: int) -> int:
        return len(self.get_user_wallets(user_id=user_id))

    def deposit(self, wallet_address: int, amount: float) -> (bool, Optional[str]):
        if amount <= 0:
            return False, "Can't deposit non-positive amount"

        uid, wallet = self._find_wallet_and_remove(wallet_address)

        if wallet is None:
            print("wallet is none")
            return False, "Can't find wallet with that address"

        wallet.deposit(amount)

        self.wallet_dict[uid].append(wallet)
        return True, None

    def withdraw(self, wallet_address: int, amount: float) -> (bool, Optional[str]):
        if amount <= 0:
            return False, "Can't withdraw non-positive amount"

        uid, wallet = self._find_wallet_and_remove(wallet_address)
        if wallet is None:
            return False, "Can't find wallet with that address"

        if wallet.get_amount() < amount:
            self.wallet_dict[uid].append(wallet)
            return False, "Not enough money"

        wallet.withdraw(amount)

        self.wallet_dict[uid].append(wallet)
        return True, None

    def _find_wallet_and_remove(self, wallet_address: int) -> (int, Optional[IWallet]):
        for uid in self.wallet_dict:
            for wallet in self.wallet_dict[uid]:
                if wallet.get_address() == wallet_address:
                    self.wallet_dict[uid].remove(wallet)
                    return uid, wallet

        return -1, None

    def wallets_belong_to_the_same_user(
        self, first_wallet_address: int, second_wallet_address: int
    ) -> bool:
        first_wallet_user = None
        second_wallet_user = None

        for uid in self.wallet_dict:
            for wallet in self.wallet_dict[uid]:
                if wallet.get_address() == first_wallet_address:
                    first_wallet_user = uid
                if wallet.get_address() == second_wallet_address:
                    second_wallet_user = uid
            if first_wallet_user is not None or second_wallet_user is not None:
                break

        if first_wallet_user is None or second_wallet_user is None:
            return False

        return first_wallet_user == second_wallet_user

    def get_user_wallets(self, user_id: int) -> List[IWallet]:
        if user_id not in self.wallet_dict:
            print(f"Current wallet: {self.wallet_dict}")
            return []

        return self.wallet_dict[user_id]

    def commit(self) -> None:
        print(f"Committed: {self.wallet_dict}")

    def rollback(self) -> None:
        print(f"Can't roll back: {self.wallet_dict}")

    @abstractmethod
    def default_wallet(self, uid: int) -> IWallet:
        pass

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass


@dataclass
class InMemoryWalletRepository(AbstractInMemoryWalletRepository):
    new_wallet_address: int = field(default=0)

    def default_wallet(self, uid: int) -> IWallet:
        self.new_wallet_address += 1
        return BitcoinWallet(
            wallet_address=self.new_wallet_address, user_id=uid, amount_BTC=1
        )
