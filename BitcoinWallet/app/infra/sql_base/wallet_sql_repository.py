import sqlite3
from abc import abstractmethod
from typing import List, Optional, Tuple

from app.core.auth.interactor import IUserRepository
from app.core.wallet.wallet import BitcoinWallet, IWallet


class AbstractWalletRepository:
    def __init__(
        self,
        db_name: str,
        user_repository: IUserRepository,
        max_number_of_wallets: int = 3,
    ):
        self.new_wallet_address = 0
        self.con = sqlite3.connect(db_name, check_same_thread=False)

        self.user_repository = user_repository

        self.max_number_of_users = max_number_of_wallets

        cursor = self.con.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS wallet 
            (wallet_address integer primary key autoincrement unique, 
            amount real, 
            user_id integer)"""
        )

        self.con.commit()
        cursor.close()

    def __del__(self) -> None:
        self.con.close()

    def create_wallet(self, api_key: str) -> Tuple[Optional[IWallet], Optional[str]]:
        uid = self.user_repository.get_user_id(api_key)

        if uid is None:
            return None, "Can't verify user"

        if self.num_wallets(user_id=uid) >= self.max_number_of_users:
            return None, f"Can't create more than ${self.max_number_of_users} wallets"

        new_wallet = self.default_wallet(uid=uid)
        try:
            cursor = self.con.cursor()
            sql_statement = """INSERT INTO wallet (amount, user_id) VALUES(?,?)"""
            cursor.execute(sql_statement, (new_wallet.get_amount(), uid))

            new_address = cursor.lastrowid
            new_wallet.set_address(new_address)

            self.commit()
            cursor.close()
            return new_wallet, None

        except sqlite3.Error as error:
            self.respond_to_sql_error(error)

        return None, "Error while accessing database"

    def get_wallet(
        self, api_key: str, address: int
    ) -> Tuple[Optional[IWallet], Optional[str]]:
        uid = self.user_repository.get_user_id(api_key=api_key)

        if uid is None:
            return None, "Can't verify user"
        result_wallet, error_str = self._get_wallet_with_address(address=address)
        if result_wallet.get_user() != uid:
            return None, "Access to wallet denied"
        return result_wallet, error_str

    def _get_wallet_with_address(
        self, address: int
    ) -> Tuple[Optional[IWallet], Optional[str]]:
        try:
            cursor = self.con.cursor()
            sql_statement = """SELECT * FROM wallet WHERE wallet_address=?"""

            cursor.execute(sql_statement, (address,))

            wallet_tuple = cursor.fetchone()

            cursor.close()

            if wallet_tuple is None:
                return None, "Wrong wallet address"
            return (
                BitcoinWallet(
                    wallet_address=wallet_tuple[0],
                    amount_BTC=wallet_tuple[1],
                    user_id=wallet_tuple[2],
                ),
                None,
            )
        except sqlite3.Error as error:
            self.respond_to_sql_error(error)

        return None, "Error while accessing database"

    def num_wallets(self, user_id: int) -> int:
        return len(self.get_user_wallets(user_id))

    def deposit(self, wallet_address: int, amount: float) -> Tuple[bool, Optional[str]]:
        if amount <= 0:
            return False, "Can't deposit non-positive amount"

        old_wallet, error_str = self._get_wallet_with_address(wallet_address)

        if error_str is not None:
            return False, error_str

        new_amount = old_wallet.get_amount() + amount

        return self._update_amount_in_wallet(
            address=wallet_address, new_amount=new_amount
        )

    def withdraw(
        self, wallet_address: int, amount: float
    ) -> Tuple[bool, Optional[str]]:
        if amount <= 0:
            return False, "Can't withdraw non-positive amount"

        old_wallet, error_str = self._get_wallet_with_address(wallet_address)

        if error_str is not None:
            return False, error_str

        if amount > old_wallet.get_amount():
            return False, "Not enough money in account"

        new_amount = old_wallet.get_amount() - amount

        return self._update_amount_in_wallet(
            address=wallet_address, new_amount=new_amount
        )

    def _update_amount_in_wallet(
        self, address: int, new_amount: float
    ) -> Tuple[bool, Optional[str]]:
        try:
            cursor = self.con.cursor()
            sql_statement = """UPDATE wallet set amount = ? WHERE wallet_address = ?"""

            cursor.execute(sql_statement, (new_amount, address))

            records = cursor.fetchall()

            result = list()

            for wallet_record in records:
                result.append(
                    BitcoinWallet(
                        wallet_address=wallet_record[0],
                        amount_BTC=wallet_record[1],
                        user_id=wallet_record[2],
                    )
                )
            cursor.close()
            return True, None
        except sqlite3.Error as error:
            self.respond_to_sql_error(error)

        return False, "Error while accessing database"

    def wallets_belong_to_the_same_user(
        self, first_wallet_address: int, second_wallet_address: int
    ) -> bool:
        first_wallet, _ = self._get_wallet_with_address(first_wallet_address)
        second_wallet, _ = self._get_wallet_with_address(second_wallet_address)

        if first_wallet is None or second_wallet is None:
            return False

        return first_wallet.get_user() == second_wallet.get_user()

    def get_user_wallets(self, user_id: int) -> List[IWallet]:
        try:
            cursor = self.con.cursor()
            sql_statement = """SELECT * FROM wallet WHERE user_id=?"""

            cursor.execute(sql_statement, (user_id,))

            records = cursor.fetchall()

            result = list()

            for wallet_record in records:
                result.append(
                    BitcoinWallet(
                        wallet_address=wallet_record[0],
                        amount_BTC=wallet_record[1],
                        user_id=wallet_record[2],
                    )
                )
            cursor.close()
            return result
        except sqlite3.Error as error:
            self.respond_to_sql_error(error)

        return []

    def respond_to_sql_error(self, error: sqlite3.Error) -> None:
        print(self.max_number_of_users)
        print(error)

    def commit(self) -> None:
        self.con.commit()

    def rollback(self) -> None:
        self.con.rollback()

    @abstractmethod
    def default_wallet(self, uid: int) -> IWallet:
        pass


class WalletSQLRepository(AbstractWalletRepository):
    def default_wallet(self, uid: int) -> IWallet:
        self.new_wallet_address += 1
        return BitcoinWallet(
            wallet_address=self.new_wallet_address, user_id=uid, amount_BTC=1
        )
