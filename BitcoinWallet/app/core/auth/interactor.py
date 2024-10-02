from dataclasses import dataclass
from typing import Optional, Protocol

from app.utils.result import Result, ResultStatus


@dataclass
class RegisterUserRequest:
    userName: str


@dataclass
class RegisterUserResponse:
    api_key: str


class IUserRepository(Protocol):
    def register_user(self, username: str) -> Result[str]:
        pass

    def get_user_id(self, api_key: str) -> Optional[int]:
        pass


@dataclass
class UserInteractor:
    user_repository: IUserRepository

    def register_user(self, user: RegisterUserRequest) -> Result[RegisterUserResponse]:
        res = self.user_repository.register_user(user.userName)
        if res.status == ResultStatus.SUCCESS and res.data is not None:
            return Result(ResultStatus.SUCCESS, RegisterUserResponse(res.data))
        else:
            return Result(res.status, exception=res.exception)
