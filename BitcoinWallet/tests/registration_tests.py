from app.core.auth.interactor import UserInteractor, RegisterUserRequest
from app.infra.api_key_generator.api_key_generator import DummyApiKeyGenerator
from app.infra.sql_base.sql_base_repository import SQLBaseRepository
from app.utils.result import ResultStatus


def test_base():
    user_sql_repo = SQLBaseRepository(":memory:", DummyApiKeyGenerator())

    user1 = user_sql_repo.register_user("vigaca1")
    assert user1.status == ResultStatus.SUCCESS

    user2 = user_sql_repo.register_user("vigaca2")
    assert user2.status == ResultStatus.SUCCESS
    assert user1.data != user2.data

    user1_clone = user_sql_repo.register_user("vigaca1")
    assert user1_clone.status == ResultStatus.SUCCESS
    assert user1.data != user1_clone.data


def test_interactor():
    user_sql_repo = SQLBaseRepository(":memory:", DummyApiKeyGenerator())
    interactor = UserInteractor(user_sql_repo)
    user1 = interactor.register_user(RegisterUserRequest("vigaca1"))
    user1_key = user1.data
    assert (
            user1.status == ResultStatus.SUCCESS
    )

    user2 = interactor.register_user(RegisterUserRequest("vigaca2"))
    user2_key = user2.data
    assert (
            user2.status == ResultStatus.SUCCESS
            and user1_key != user2_key
    )

    user1_clone = interactor.register_user(RegisterUserRequest("vigaca1"))
    user1_clone_key = user1_clone.data
    assert (
            user1_clone.status == ResultStatus.SUCCESS
            and user1_key != user1_clone_key
    )
