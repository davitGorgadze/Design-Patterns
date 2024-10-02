from dataclasses import dataclass
from typing import List, Protocol, Set

from app.core.auth.interactor import IUserRepository
from app.core.exceptions import (
    TransactionError,
    UserNotFoundError,
    WalletNotAccessibleError,
)
from app.core.statistics.interactor import IProfitsRepository
from app.core.transaction.transaction import (
    ITransaction,
    ITransactionRepository,
    SimpleTransaction,
    TransactionBetweenUsers,
)
from app.core.wallet.wallet import IWalletRepository
from app.utils.result import Result, ResultStatus


@dataclass
class MakeTransactionRequest:
    api_key: str
    from_wallet_address: int
    to_wallet_address: int
    balance: float


@dataclass
class MakeTransactionResponse:
    transaction_id: int


@dataclass
class WalletTransactionsRequest:
    api_key: str
    wallet_address: int


@dataclass
class UserTransactionsRequest:
    api_key: str


@dataclass
class UserTransactionsResponse:
    user_transactions: List[ITransaction]


@dataclass
class WalletTransactionsResponse:
    transactions: List[ITransaction]


# could be used to send SMS or E-mail to clients
class IObserver(Protocol):
    def on_transaction_succeeded(self, transaction: ITransaction) -> None:
        pass


@dataclass
class Observable:
    observers: Set[IObserver]

    def attach(self, observer: IObserver) -> None:
        self.observers.add(observer)

    def detach(self, observer: IObserver) -> None:
        self.observers.remove(observer)

    def notify_transaction_succeeded(self, transaction: ITransaction) -> None:
        for observer in self.observers:
            observer.on_transaction_succeeded(transaction)


@dataclass
class TransactionInteractor(Observable):
    transactions_repository: ITransactionRepository
    wallets_repository: IWalletRepository
    user_repository: IUserRepository
    profits_repository: IProfitsRepository

    # tried to implement transaction logic but didn't work out well
    def fire_transaction(
        self, request: MakeTransactionRequest
    ) -> Result[MakeTransactionResponse]:
        try:
            user_id = self.user_repository.get_user_id(request.api_key)
            if user_id is None:
                raise UserNotFoundError()
            user_wallets = self.wallets_repository.get_user_wallets(user_id)
            for wallet in user_wallets:
                if wallet.get_address() == request.from_wallet_address:
                    result = self._make_transaction(request)
                    if result.status != ResultStatus.SUCCESS:
                        raise result.exception
                    # self.wallets_repository.commit()
                    # self.transactions_repository.commit()
                    # self.profits_repository.commit()
                    return Result(ResultStatus.SUCCESS, result.data)
            raise WalletNotAccessibleError()
        except TransactionError as t:
            # self.wallets_repository.rollback()
            # self.transactions_repository.rollback()
            # self.profits_repository.rollback()
            return Result(ResultStatus.FAIL, exception=t)
        except Exception as e:
            return Result(ResultStatus.FAIL, exception=e)

    def _make_transaction(self, request: MakeTransactionRequest) -> Result[int]:
        sender, receiver, balance = (
            request.from_wallet_address,
            request.to_wallet_address,
            request.balance,
        )
        success, message = self.wallets_repository.withdraw(sender, balance)
        if not success:
            return Result(ResultStatus.FAIL, exception=TransactionError(message))
        success, message = self.wallets_repository.deposit(receiver, balance)
        if not success:
            return Result(ResultStatus.FAIL, exception=TransactionError(message))
        curr_transaction = SimpleTransaction(sender, receiver, balance)
        if not self.wallets_repository.wallets_belong_to_the_same_user(
            sender, receiver
        ):
            curr_transaction = TransactionBetweenUsers(curr_transaction)
        self.wallets_repository.commit()
        result = self.transactions_repository.create(curr_transaction)
        if result.status != ResultStatus.SUCCESS:
            return Result(
                ResultStatus.FAIL,
                exception=TransactionError(
                    "error while inserting row in transactions table"
                ),
            )
        self.transactions_repository.commit()
        curr_transaction.transaction_id = result.data
        system_profit = curr_transaction.calculate_system_profit()
        result = self.profits_repository.add_system_profit(
            curr_transaction.transaction_id, system_profit
        )
        if result.status != ResultStatus.SUCCESS:
            return Result(
                ResultStatus.FAIL,
                exception=TransactionError(
                    "error while inserting row in profits table"
                ),
            )
        self.profits_repository.commit()
        return Result(ResultStatus.SUCCESS, curr_transaction.transaction_id)

    def get_wallet_transactions(
        self, request: WalletTransactionsRequest
    ) -> Result[WalletTransactionsResponse]:
        try:
            user_id = self.user_repository.get_user_id(request.api_key)
            if user_id is None:
                raise UserNotFoundError()
            result = self.transactions_repository.get_wallet_transactions(
                request.wallet_address
            )
            if result.status == ResultStatus.FAIL:
                raise result.exception
            response = WalletTransactionsResponse(result.data)
            return Result(ResultStatus.SUCCESS, response)
        except Exception as e:
            return Result(ResultStatus.FAIL, exception=e)

    def get_user_transactions(
        self, requset: UserTransactionsRequest
    ) -> Result[UserTransactionsResponse]:
        try:
            user_id = self.user_repository.get_user_id(requset.api_key)
            if user_id is None:
                raise UserNotFoundError()
            user_wallets = self.wallets_repository.get_user_wallets(user_id)
            user_transactions = []
            for wallet in user_wallets:
                wallet_transactions = (
                    self.transactions_repository.get_wallet_transactions(
                        wallet.get_address()
                    ).data
                )
                for transaction in wallet_transactions:
                    if transaction not in user_transactions:
                        user_transactions.append(transaction)
            response = UserTransactionsResponse(user_transactions)
            return Result(ResultStatus.SUCCESS, response)
        except Exception as e:
            return Result(ResultStatus.FAIL, exception=e)
