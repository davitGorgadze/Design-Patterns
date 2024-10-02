import pytest

from app.core.auth.interactor import IUserRepository
from app.core.statistics.interactor import IProfitsRepository
from app.core.transaction.interactor import (
    ITransactionRepository,
    TransactionInteractor,
    WalletTransactionsRequest,
)
from app.core.transaction.transaction import SimpleTransaction, TransactionBetweenUsers
from app.core.wallet.wallet import IWalletRepository
from app.infra.api_key_generator.api_key_generator import DummyApiKeyGenerator
from app.infra.in_memory.in_memory_transaction_repository import (
    InMemoryTransactionRepository,
)
from app.infra.in_memory.profits_in_memory_repository import ProfitsInMemoryRepository
from app.infra.in_memory.wallet_in_memory_repository import InMemoryWalletRepository
from app.infra.sql_base.sql_base_repository import SQLBaseRepository
from app.utils.result import ResultStatus


@pytest.fixture
def in_memory_transaction_repository() -> ITransactionRepository:
    repository = InMemoryTransactionRepository()
    return repository


@pytest.fixture
def users_repository() -> IUserRepository:
    repository = SQLBaseRepository(
        db_name=":memory:", api_generator=DummyApiKeyGenerator()
    )
    return repository


@pytest.fixture
def in_memory_wallet_repository(users_repository: IUserRepository) -> IWalletRepository:
    repository = InMemoryWalletRepository(
        max_number_of_wallets=3, user_repository=users_repository
    )
    return repository


def test_wallet_transactions(
    in_memory_transaction_repository: ITransactionRepository,
    users_repository: IUserRepository,
    in_memory_wallet_repository: IWalletRepository,
) -> None:
    api_key_result = users_repository.register_user("Ilia")
    assert api_key_result.status == ResultStatus.SUCCESS

    wallet1, msg = in_memory_wallet_repository.create_wallet(api_key_result.data)
    assert wallet1 is not None

    wallet2, msg = in_memory_wallet_repository.create_wallet(api_key_result.data)
    assert wallet2 is not None

    wallet1.deposit(10)
    wallet2.deposit(10)

    interactor = TransactionInteractor(
        set(),
        transactions_repository=in_memory_transaction_repository,
        user_repository=users_repository,
        wallets_repository=in_memory_wallet_repository,
        profits_repository=ProfitsInMemoryRepository(),
    )

    t1 = SimpleTransaction(wallet1.get_address(), wallet2.get_address(), 2)
    t2 = SimpleTransaction(wallet2.get_address(), wallet1.get_address(), 5)

    transaction_1_result = in_memory_transaction_repository.create(t1)
    assert transaction_1_result.status == ResultStatus.SUCCESS
    t1.transaction_id = transaction_1_result.data

    transaction_2_result = in_memory_transaction_repository.create(t2)
    assert transaction_2_result.status == ResultStatus.SUCCESS
    t2.transaction_id = transaction_2_result.data

    wallet_transactions_result = interactor.get_wallet_transactions(
        WalletTransactionsRequest(api_key_result.data, wallet1.get_address())
    )
    assert wallet_transactions_result.status == ResultStatus.SUCCESS
    assert len(wallet_transactions_result.data.transactions) == 2
    assert t1 in wallet_transactions_result.data.transactions
    assert t2 in wallet_transactions_result.data.transactions
