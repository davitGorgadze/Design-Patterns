from typing import List

from app.core.statistics.interactor import IProfit, IProfitsRepository
from app.utils.result import Result, ResultStatus


class ProfitsInMemoryRepository(IProfitsRepository):
    def __init__(self) -> None:
        self.profits_db: List[IProfit] = []
        self.id_counter: int = 1

    def add_system_profit(
        self, transaction_id: int, system_profit: float
    ) -> Result[int]:
        try:
            profit: IProfit = IProfit(self.id_counter, transaction_id, system_profit)
            self.id_counter += 1
            self.profits_db.append(profit)
            return Result(status=ResultStatus.SUCCESS, data=profit.id)
        except Exception as e:
            return Result(status=ResultStatus.FAIL, exception=e)

    def get_total_profit(self) -> Result[float]:
        try:
            total_profit: float = sum(
                [profit.system_profit for profit in self.profits_db]
            )
            return Result(status=ResultStatus.SUCCESS, data=total_profit)
        except Exception as e:
            return Result(status=ResultStatus.FAIL, exception=e)

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass
