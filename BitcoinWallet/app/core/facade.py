from dataclasses import dataclass

from app.core.auth.interactor import (
    IUserRepository,
    RegisterUserRequest,
    RegisterUserResponse,
    UserInteractor,
)
from app.core.statistics.interactor import (
    AddProfitRequest,
    AddProfitResponse,
    IProfitsRepository,
    StatisticsInteractor,
    StatisticsRequest,
    StatisticsResponse,
)
from app.core.transaction.interactor import (
    IWalletRepository,
    MakeTransactionRequest,
    MakeTransactionResponse,
    TransactionInteractor,
    UserTransactionsRequest,
    UserTransactionsResponse,
    WalletTransactionsRequest,
    WalletTransactionsResponse,
)
from app.core.transaction.transaction import ITransactionRepository
from app.core.wallet.interactor import (
    CreateWalletRequest,
    GetWalletRequest,
    GetWalletResponse,
    WalletInteractor,
)
from app.utils.result import Result


@dataclass
class WalletService:
    user_interactor: UserInteractor
    transactions_interactor: TransactionInteractor
    wallet_interactor: WalletInteractor
    statistics_interactor: StatisticsInteractor

    def register_user(self, user: RegisterUserRequest) -> Result[RegisterUserResponse]:
        return self.user_interactor.register_user(user)

    def make_transaction(
        self, request: MakeTransactionRequest
    ) -> Result[MakeTransactionResponse]:
        return self.transactions_interactor.fire_transaction(request)

    def get_wallet_transactions(
        self, request: WalletTransactionsRequest
    ) -> Result[WalletTransactionsResponse]:
        return self.transactions_interactor.get_wallet_transactions(request)

    def get_user_transactions(
        self, request: UserTransactionsRequest
    ) -> Result[UserTransactionsResponse]:
        return self.transactions_interactor.get_user_transactions(request)

    def create_wallet(self, request: CreateWalletRequest) -> Result[GetWalletResponse]:
        return self.wallet_interactor.create_new_wallet(request=request)

    def get_wallet(self, request: GetWalletRequest) -> Result[GetWalletResponse]:
        return self.wallet_interactor.get_wallet(request=request)

    def add_profit(self, request: AddProfitRequest) -> Result[AddProfitResponse]:
        return self.statistics_interactor.add_profit(request)

    def get_statistics(self, request: StatisticsRequest) -> Result[StatisticsResponse]:
        return self.statistics_interactor.get_statistics(request)

    @classmethod
    def create(
        cls,
        user_repository: IUserRepository,
        transaction_repository: ITransactionRepository,
        wallet_repository: IWalletRepository,
        profits_repository: IProfitsRepository,
    ) -> "WalletService":
        return cls(
            user_interactor=UserInteractor(user_repository=user_repository),
            transactions_interactor=TransactionInteractor(
                set(),
                transactions_repository=transaction_repository,
                wallets_repository=wallet_repository,
                user_repository=user_repository,
                profits_repository=profits_repository,
            ),
            wallet_interactor=WalletInteractor(wallet_repository=wallet_repository),
            statistics_interactor=StatisticsInteractor(
                profits_repository=profits_repository,
                transactions_repository=transaction_repository,
                admin_keys=["admin_1", "admin_2", "admin_3"],
            ),
        )
