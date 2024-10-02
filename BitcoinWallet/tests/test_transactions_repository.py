from app.core.transaction.transaction import SimpleTransaction
from app.infra.in_memory.in_memory_transaction_repository import InMemoryTransactionRepository
from app.infra.sql_base.sql_transaction_repository import SQLTransactionRepository
from app.utils.result import ResultStatus


def test_in_memory_transactions_repository() -> None:
    repository = InMemoryTransactionRepository()
    assert repository.get_transaction_count().data == 0
    result = repository.create(SimpleTransaction(1, 2, 5))
    assert result.status == ResultStatus.SUCCESS
    assert repository.get_transaction_count().data == 1
    wallet_1_transactions = repository.get_wallet_transactions(1)
    wallet_2_transactions = repository.get_wallet_transactions(2)
    assert wallet_1_transactions.status == ResultStatus.SUCCESS
    assert wallet_2_transactions.status == ResultStatus.SUCCESS
    assert len(wallet_2_transactions.data) == 1
    assert len(wallet_1_transactions.data) == 1
    assert wallet_2_transactions.data[0] == SimpleTransaction(1, 2, 5, 0)


def test_sql_transactions_repository() -> None:
    repository = SQLTransactionRepository(":memory:")
    transaction1 = SimpleTransaction(1, 2, 5)
    transaction2 = SimpleTransaction(2, 1, 5)
    assert repository.get_transaction_count().data == 0
    result1 = repository.create(transaction1)
    assert result1.status == ResultStatus.SUCCESS
    assert repository.get_transaction_count().data == 1
    transaction1.transaction_id = result1.data

    result2 = repository.create(transaction2)
    assert result2.status == ResultStatus.SUCCESS
    assert repository.get_transaction_count().data == 2
    transaction2.transaction_id = result2.data

    wallet_1_transactions_result = repository.get_wallet_transactions(1)
    assert wallet_1_transactions_result.status == ResultStatus.SUCCESS

    wallet_2_transactions_result = repository.get_wallet_transactions(2)
    assert wallet_2_transactions_result.status == ResultStatus.SUCCESS

    assert len(wallet_1_transactions_result.data) == 2
    assert len(wallet_2_transactions_result.data) == 2

    assert transaction1 in wallet_2_transactions_result.data
    assert transaction2 in wallet_2_transactions_result.data



