from fastapi import FastAPI

from app.core.facade import WalletService
from app.core.auth.interactor import IUserRepository
from app.core.transaction.transaction import ITransactionRepository
from app.core.wallet.wallet import IWalletRepository
from app.infra.api_key_generator.api_key_generator import DummyApiKeyGenerator
from app.infra.fastapi.auth import auth_api
from app.infra.fastapi.transactions import transactions_api

from app.infra.fastapi.wallet_api import wallet_api

from app.infra.sql_base.sql_base_repository import SQLBaseRepository
from app.infra.sql_base.sql_transaction_repository import SQLTransactionRepository
from app.infra.sql_base.wallet_sql_repository import WalletSQLRepository
from app.core.statistics.interactor import IProfitsRepository
from app.infra.fastapi.statistics import statistics_api
from app.infra.sql_base.profits_sql_repository import ProfitsRepository


def setup() -> FastAPI:
    app = FastAPI()
    app.include_router(auth_api)
    app.include_router(wallet_api)
    app.include_router(transactions_api)
    app.include_router(statistics_api)

    user_repository = setup_user_repository()
    wallet_repository = setup_wallet_repository(user_repository=user_repository)
    transaction_repository = setup_transactions_repository()
    profits_repository = setup_profits_repository()
    app.state.core = WalletService.create(user_repository=user_repository,
                                          wallet_repository=wallet_repository,
                                          transaction_repository=transaction_repository,
                                          profits_repository=profits_repository)

    return app


def setup_user_repository() -> IUserRepository:
    repository = SQLBaseRepository.create("wallets.db", DummyApiKeyGenerator())
    return repository


def setup_wallet_repository(user_repository: IUserRepository) -> IWalletRepository:
    repository = WalletSQLRepository(db_name="wallets.db", user_repository=user_repository)
    return repository


def setup_transactions_repository() -> ITransactionRepository:
    return SQLTransactionRepository(db_name="wallets.db")


def setup_profits_repository() -> IProfitsRepository:
    repository = ProfitsRepository(db_name="wallets.db")
    return repository
