from dataclasses import dataclass
from typing import List

from app.core.transaction.transaction import ITransactionRepository
from app.utils.result import Result, ResultStatus


@dataclass
class IProfit:
    id: int
    transaction_id: int
    system_profit: float


@dataclass
class AddProfitRequest:
    transaction_id: int
    system_profit: float


@dataclass
class AddProfitResponse:
    id: int


@dataclass
class StatisticsRequest:
    user_key: str


@dataclass
class StatisticsResponse:
    transaction_count: int
    total_profit: float


class IProfitsRepository:
    def add_system_profit(
        self, transaction_id: int, system_profit: float
    ) -> Result[int]:
        pass

    def get_total_profit(self) -> Result[float]:
        pass

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass


@dataclass
class StatisticsInteractor:
    profits_repository: IProfitsRepository
    transactions_repository: ITransactionRepository
    admin_keys: List[str]

    def add_profit(self, profit: AddProfitRequest) -> Result[AddProfitResponse]:

        res = self.profits_repository.add_system_profit(
            profit.transaction_id, profit.system_profit
        )
        if res.status == ResultStatus.SUCCESS and res.data is not None:
            return Result(ResultStatus.SUCCESS, AddProfitResponse(res.data))
        else:
            return Result(res.status, exception=res.exception)

    def get_statistics(self, user: StatisticsRequest) -> Result[StatisticsResponse]:
        if user.user_key not in self.admin_keys:
            return Result(ResultStatus.FAIL)

        profits = self.profits_repository.get_total_profit()
        transactions = self.transactions_repository.get_transaction_count()
        if (
            profits.status == ResultStatus.SUCCESS
            and profits.data is not None
            and transactions.status == ResultStatus.SUCCESS
            and transactions.data is not None
        ):
            return Result(
                ResultStatus.SUCCESS,
                StatisticsResponse(transactions.data, profits.data),
            )
        else:
            return Result(ResultStatus.FAIL)
