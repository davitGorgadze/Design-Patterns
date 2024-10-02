import sqlite3

from app.core.statistics.interactor import IProfitsRepository
from app.utils.result import Result, ResultStatus


class ProfitsRepository(IProfitsRepository):
    def __init__(self, db_name: str) -> None:
        super().__init__()
        self.con = sqlite3.connect(db_name, check_same_thread=False)
        self.cur = self.con.cursor()
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS profits (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                transaction_id INTEGER, 
                system_profit REAL
            )
            """
        )

    def add_system_profit(
        self, transaction_id: int, system_profit: float
    ) -> Result[int]:
        """
        Adds action to the profits table.
        """
        try:
            self.cur.execute(
                """INSERT INTO profits (transaction_id, system_profit) values (?, ?)""",
                (transaction_id, system_profit),
            )
            return Result(ResultStatus.SUCCESS, data=self.cur.lastrowid)
        except Exception as e:
            return Result(ResultStatus.FAIL, exception=e)

    def get_total_profit(self) -> Result[float]:
        """
        Returns total profit. 0 if profits table is empty.
        """
        try:
            profit: float = self.cur.execute(
                f"""
                SELECT SUM(system_profit) FROM profits
                """
            ).fetchone()[0]
            profit = profit if profit is not None else 0

            return Result(ResultStatus.SUCCESS, data=profit)
        except Exception as e:
            return Result(ResultStatus.FAIL, exception=e)

    def commit(self) -> None:
        self.con.commit()

    def rollback(self) -> None:
        self.con.rollback()
