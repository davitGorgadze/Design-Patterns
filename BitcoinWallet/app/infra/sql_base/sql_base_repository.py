import sqlite3
from typing import Optional

from app.core.auth.interactor import IUserRepository
from app.infra.api_key_generator.api_key_generator import IApiKeyGenerator
from app.utils.result import Result, ResultStatus


class SQLBaseRepository(IUserRepository):
    key_generator: IApiKeyGenerator

    def __init__(self, db_name: str, api_generator: IApiKeyGenerator) -> None:
        self.key_generator = api_generator
        self.con = sqlite3.connect(db_name, check_same_thread=False)
        self.cur = self.con.cursor()
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS users (id integer primary key, username text, api_key text)"""
        )

    def __del__(self) -> None:
        self.con.close()

    def register_user(self, username: str) -> Result[str]:
        try:
            api_key = self.key_generator.generate_key(username)
            self.cur.execute(
                """insert into users (username, api_key) values (?, ?)""",
                (username, api_key),
            )
            self.con.commit()
            return Result(ResultStatus.SUCCESS, api_key)
        except Exception as e:
            return Result(ResultStatus.FAIL, exception=e)

    # need to implement this
    def get_user_id(self, api_key) -> Optional[int]:
        try:
            self.cur.execute("""select * from users where api_key = ?""", (api_key,))
            result = self.cur.fetchone()
            if result is None:
                return None
            return result[0]
        except Exception as e:
            return None

    @classmethod
    def create(
        cls, db_name: str, api_generator: IApiKeyGenerator
    ) -> "SQLBaseRepository":
        return cls(db_name=db_name, api_generator=api_generator)
