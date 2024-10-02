from app.core.auth.interactor import IUserRepository
from app.infra.api_key_generator.api_key_generator import DummyApiKeyGenerator
from app.infra.in_memory.wallet_in_memory_repository import InMemoryWalletRepository
from app.infra.sql_base.sql_base_repository import SQLBaseRepository


def get_dummy_user_repo():
    user_repo = SQLBaseRepository.create(":memory:",
                                         api_generator=DummyApiKeyGenerator())
    api_k1 = user_repo.register_user("user1")
    api_k2 = user_repo.register_user("user2")
    api_k3 = user_repo.register_user("user3")
    return user_repo, api_k1, api_k2, api_k3


def get_dummy_wallet_repository(user_repo: IUserRepository, max_wallet_count: int = 3):
    return InMemoryWalletRepository(user_repository=user_repo,
                                    max_number_of_wallets=max_wallet_count)


def test_initialization():
    dummy_user_repo, _, _, _ = get_dummy_user_repo()
    repo = get_dummy_wallet_repository(user_repo=dummy_user_repo)
    assert len(repo.wallet_dict) == 0


def test_create_wallet_with_wrong_api_key():
    dummy_user_repo, api_k1, api_k2, api_k3 = get_dummy_user_repo()
    repo = get_dummy_wallet_repository(user_repo=dummy_user_repo)

    wallet = repo.create_wallet(api_key=api_k1.data + api_k2.data + api_k3.data)
    assert wallet[0] is None
    assert wallet[1] is not None


def test_create_wallet():
    dummy_user_repo, api_k1, api_k2, api_k3 = get_dummy_user_repo()
    repo = get_dummy_wallet_repository(dummy_user_repo)

    wallet1 = repo.create_wallet(api_key=api_k1.data)
    wallet2 = repo.create_wallet(api_key=api_k2.data)
    wallet3 = repo.create_wallet(api_key=api_k3.data)
    assert wallet1[0] is not None
    assert wallet2[0] is not None
    assert wallet3[0] is not None


def test_maximum_wallet_count_works():
    dummy_user_repo, api_k1, api_k2, _ = get_dummy_user_repo()
    repo = get_dummy_wallet_repository(user_repo=dummy_user_repo, max_wallet_count=2)

    wallet1 = repo.create_wallet(api_key=api_k1.data)
    wallet2 = repo.create_wallet(api_key=api_k1.data)
    assert wallet1 is not None
    assert wallet2 is not None
    assert len(repo.get_user_wallets(user_id=dummy_user_repo.get_user_id(api_k1.data))) == 2
    wallet3 = repo.create_wallet(api_key=api_k1.data)
    assert wallet3 is None
    assert len(repo.get_user_wallets(user_id=dummy_user_repo.get_user_id(api_k1.data))) == 2


def test_get_wallet():
    dummy_user_repo, api_k1, api_k2, _ = get_dummy_user_repo()
    repo = get_dummy_wallet_repository(user_repo=dummy_user_repo, max_wallet_count=2)

    wallet1 = repo.create_wallet(api_key=api_k1.data)

    assert wallet1 == repo.get_wallet(api_k1.data, wallet1.get_address())
    assert wallet1 != repo.get_wallet(api_k2.data, wallet1.get_address())


def test_num_wallets():
    dummy_user_repo, api_k1, api_k2, _ = get_dummy_user_repo()
    repo = get_dummy_wallet_repository(user_repo=dummy_user_repo, max_wallet_count=2)
    assert repo.num_wallets(dummy_user_repo.get_user_id(api_k1.data)) == 0
    wallet1 = repo.create_wallet(api_key=api_k1.data)
    assert repo.num_wallets(dummy_user_repo.get_user_id(api_k1.data)) == 1
    wallet2 = repo.create_wallet(api_key=api_k1.data)
    assert repo.num_wallets(dummy_user_repo.get_user_id(api_k1.data)) == 2


def test_amount_in_default_wallet_is_correct():
    dummy_user_repo, api_k1, api_k2, _ = get_dummy_user_repo()
    repo = get_dummy_wallet_repository(user_repo=dummy_user_repo, max_wallet_count=2)

    wallet1 = repo.create_wallet(api_key=api_k1.data)
    assert wallet1.get_amount() == repo.default_wallet(0).get_amount()


def test_deposit():
    dummy_user_repo, api_k1, _, _ = get_dummy_user_repo()
    repo = get_dummy_wallet_repository(user_repo=dummy_user_repo, max_wallet_count=2)

    wallet1 = repo.create_wallet(api_key=api_k1.data)

    starting_amount = wallet1.get_amount()
    to_deposit = 20
    repo.deposit(wallet_address=wallet1.get_address(), amount=to_deposit)

    assert repo.get_wallet(api_k1.data, address=wallet1.get_address()).get_amount() == starting_amount + to_deposit


def test_deposit_negative_does_nothing():
    dummy_user_repo, api_k1, _, _ = get_dummy_user_repo()
    repo = get_dummy_wallet_repository(user_repo=dummy_user_repo, max_wallet_count=2)

    wallet1 = repo.create_wallet(api_key=api_k1.data)

    starting_amount = wallet1.get_amount()
    to_deposit = -20
    assert not repo.deposit(wallet_address=wallet1.get_address(), amount=to_deposit)

    assert repo.get_wallet(api_k1.data, address=wallet1.get_address()).get_amount() == starting_amount


def test_withdraw_more_than_in_account():
    dummy_user_repo, api_k1, _, _ = get_dummy_user_repo()
    repo = get_dummy_wallet_repository(user_repo=dummy_user_repo, max_wallet_count=2)

    wallet1 = repo.create_wallet(api_key=api_k1.data)
    starting_amount = wallet1.get_amount()
    to_withdraw = starting_amount + 10

    assert not repo.withdraw(wallet_address=wallet1.get_address(), amount=to_withdraw)
    assert repo.get_wallet(api_k1.data, address=wallet1.get_address()).get_amount() == starting_amount


def test_withdraw_negative_amount():
    dummy_user_repo, api_k1, _, _ = get_dummy_user_repo()
    repo = get_dummy_wallet_repository(user_repo=dummy_user_repo, max_wallet_count=2)

    wallet1 = repo.create_wallet(api_key=api_k1.data)
    starting_amount = wallet1.get_amount()
    to_withdraw = -10

    assert not repo.withdraw(wallet_address=wallet1.get_address(), amount=to_withdraw)
    assert repo.get_wallet(api_k1.data, address=wallet1.get_address()).get_amount() == starting_amount


def test_withdraw():
    dummy_user_repo, api_k1, _, _ = get_dummy_user_repo()
    repo = get_dummy_wallet_repository(user_repo=dummy_user_repo, max_wallet_count=2)

    wallet1 = repo.create_wallet(api_key=api_k1.data)

    assert repo.deposit(wallet_address=wallet1.get_address(), amount=10)

    starting_amount = wallet1.get_amount()
    to_withdraw = 5

    assert repo.withdraw(wallet_address=wallet1.get_address(), amount=to_withdraw)
    assert repo.get_wallet(api_k1.data, address=wallet1.get_address()).get_amount() == starting_amount - to_withdraw


def test_wallets_belong_to_same_user():
    dummy_user_repo, api_k1, api_k2, api_k3 = get_dummy_user_repo()
    repo = get_dummy_wallet_repository(dummy_user_repo)

    wallet1 = repo.create_wallet(api_key=api_k1.data)
    wallet2 = repo.create_wallet(api_key=api_k2.data)
    wallet3 = repo.create_wallet(api_key=api_k3.data)
    wallet4 = repo.create_wallet(api_key=api_k1.data)
    wallet5 = repo.create_wallet(api_key=api_k2.data)

    assert not repo.wallets_belong_to_the_same_user(wallet1.get_address(), wallet2.get_address())
    assert not repo.wallets_belong_to_the_same_user(wallet1.get_address(), wallet3.get_address())

    assert not repo.wallets_belong_to_the_same_user(wallet2.get_address(), wallet4.get_address())
    assert not repo.wallets_belong_to_the_same_user(wallet3.get_address(), wallet4.get_address())

    assert repo.wallets_belong_to_the_same_user(wallet1.get_address(), wallet4.get_address())
    assert repo.wallets_belong_to_the_same_user(wallet2.get_address(), wallet5.get_address())


def test_get_user_wallets():

    dummy_user_repo, api_k1, _, _ = get_dummy_user_repo()
    repo = get_dummy_wallet_repository(dummy_user_repo)

    wallet1 = repo.create_wallet(api_key=api_k1.data)
    assert len(repo.get_user_wallets(dummy_user_repo.get_user_id(api_k1.data))) == 1
    assert repo.get_user_wallets(dummy_user_repo.get_user_id(api_k1.data))[0] == wallet1

    wallet2 = repo.create_wallet(api_key=api_k1.data)

    assert len(repo.get_user_wallets(dummy_user_repo.get_user_id(api_k1.data))) == 2
    assert wallet1 in repo.get_user_wallets(dummy_user_repo.get_user_id(api_k1.data))
    assert wallet2 in repo.get_user_wallets(dummy_user_repo.get_user_id(api_k1.data))
