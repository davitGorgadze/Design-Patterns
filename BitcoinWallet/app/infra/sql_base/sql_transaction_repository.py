import sqlite3
from typing import List

from app.core.transaction.transaction import ITransaction, SimpleTransaction
from app.utils.result import Result, ResultStatus


class SQLTransactionRepository:
    def __init__(self, db_name: str) -> None:
        self.connection = sqlite3.connect(db_name, check_same_thread=False)
        cursor = self.connection.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS transactions
            (id integer primary key autoincrement,
             sender integer,
             receiver integer,
             balance real)"""
        )
        self.commit()

    def __del__(self) -> None:
        self.connection.close()

    def create(self, transaction: ITransaction) -> Result[int]:
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """INSERT INTO transactions (sender, receiver, balance) 
                values (?, ?, ?)""",
                (
                    transaction.get_sender_address(),
                    transaction.get_receiver_address(),
                    transaction.get_balance(),
                ),
            )
            return Result(ResultStatus.SUCCESS, cursor.lastrowid)
        except Exception as e:
            print(e)
            return Result(ResultStatus.FAIL, exception=e)

    def get_wallet_transactions(
        self, wallet_address: int
    ) -> Result[List[ITransaction]]:
        try:
            query_result = self.connection.execute(
                """SELECT * FROM transactions t WHERE t.sender = (?) OR t.receiver = (?)""",
                (wallet_address, wallet_address),
            )
            result: List[ITransaction] = []
            for row in query_result:
                result.append(SimpleTransaction(row[1], row[2], row[3], row[0]))
            return Result(ResultStatus.SUCCESS, result)
        except Exception as e:
            return Result(ResultStatus.FAIL, exception=e)

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        self.connection.rollback()

    def get_transaction_count(self) -> Result[int]:
        result: int = self.connection.execute(
            """SELECT COUNT(*) FROM transactions t"""
        ).fetchone()[0]
        return Result(ResultStatus.SUCCESS, result)
