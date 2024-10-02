from dataclasses import dataclass, field
from typing import List

from app.core.transaction.transaction import ITransaction
from app.utils.result import Result, ResultStatus


@dataclass
class InMemoryTransactionRepository:
    # bad idea but works as long as concurency is out of scope
    transactions_db: List[ITransaction] = field(default_factory=list)
    id_counter: int = field(default=0)

    # return newly created transaction's id
    def create(self, transaction: ITransaction) -> Result[int]:
        try:
            transaction.transaction_id = self.id_counter
            self.id_counter += 1
            self.transactions_db.append(transaction)
            return Result(ResultStatus.SUCCESS, transaction.transaction_id)
        except Exception as e:
            return Result(ResultStatus.FAIL, exception=e)

    def get_wallet_transactions(
        self, wallet_address: int
    ) -> Result[List[ITransaction]]:
        result = list()
        for transaction in self.transactions_db:
            if (
                transaction.get_sender_address() == wallet_address
                or transaction.get_receiver_address() == wallet_address
            ):
                result.append(transaction)
        return Result(ResultStatus.SUCCESS, result)

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass

    def get_transaction_count(self) -> Result[int]:
        return Result(ResultStatus.SUCCESS, len(self.transactions_db))
