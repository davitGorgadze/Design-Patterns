from app.core.auth.interactor import IUserRepository
from app.core.wallet.Converter import WrongConverter
from app.core.wallet.interactor import WalletInteractor, CreateWalletRequest, GetWalletRequest
from app.utils.result import ResultStatus
from tests.wallet.wallet_repositorry_tests import get_dummy_wallet_repository, get_dummy_user_repo


def get_dummy_interactor(user_repo: IUserRepository):
    wallet_repo = get_dummy_wallet_repository(user_repo=user_repo, max_wallet_count=3)
    return WalletInteractor(wallet_repo, converter=WrongConverter()), user_repo, wallet_repo


def test_create_new_wallet():
    user_repo, api_k1, api_k2, api_k3 = get_dummy_user_repo()
    interactor, user_repo, wallet_repo = get_dummy_interactor(user_repo)

    result = interactor.create_new_wallet(CreateWalletRequest(api_k1.data))

    assert result.status == ResultStatus.SUCCESS
    assert result.data is not None
    assert result.data.amount_BTC * WrongConverter().get_BTC_to_USD_conversion_rate() == result.data.amount_USD


def test_create_new_wallet_with_wrong_api_key():
    user_repo, api_k1, api_k2, api_k3 = get_dummy_user_repo()
    interactor, user_repo, wallet_repo = get_dummy_interactor(user_repo)

    result = interactor.create_new_wallet(CreateWalletRequest(api_k1.data + api_k2.data + api_k3.data))

    assert result.status == ResultStatus.FAIL


def test_creating_more_than_allowed_number_of_wallets():
    user_repo, api_k1, api_k2, api_k3 = get_dummy_user_repo()
    interactor, user_repo, wallet_repo = get_dummy_interactor(user_repo)

    result1 = interactor.create_new_wallet(CreateWalletRequest(api_k1.data))
    result2 = interactor.create_new_wallet(CreateWalletRequest(api_k1.data))
    result3 = interactor.create_new_wallet(CreateWalletRequest(api_k1.data))
    result4 = interactor.create_new_wallet(CreateWalletRequest(api_k1.data))

    assert result1.status == ResultStatus.SUCCESS
    assert result2.status == ResultStatus.SUCCESS
    assert result3.status == ResultStatus.SUCCESS
    assert result4.status == ResultStatus.FAIL


def test_get_wallet():
    user_repo, api_k1, api_k2, api_k3 = get_dummy_user_repo()
    interactor, user_repo, wallet_repo = get_dummy_interactor(user_repo)

    result_creation = interactor.create_new_wallet(CreateWalletRequest(api_k1.data))

    wallet_address = result_creation.data.wallet_address

    result = interactor.get_wallet(GetWalletRequest(api_key=api_k1.data, wallet_address=wallet_address))

    assert result.status == ResultStatus.SUCCESS


def test_get_wrong_wallet():
    user_repo, api_k1, api_k2, api_k3 = get_dummy_user_repo()
    interactor, user_repo, wallet_repo = get_dummy_interactor(user_repo)

    result_creation = interactor.create_new_wallet(CreateWalletRequest(api_k1.data))

    wallet_address = result_creation.data.wallet_address + 20

    result = interactor.get_wallet(GetWalletRequest(api_key=api_k1.data, wallet_address=wallet_address))

    assert result.status == ResultStatus.FAIL


def test_get_wallet_with_wrong_api_key():
    user_repo, api_k1, api_k2, api_k3 = get_dummy_user_repo()
    interactor, user_repo, wallet_repo = get_dummy_interactor(user_repo)

    result_creation = interactor.create_new_wallet(CreateWalletRequest(api_k1.data))

    wallet_address = result_creation.data.wallet_address

    result = interactor.get_wallet(GetWalletRequest(api_key=api_k2.data, wallet_address=wallet_address))

    assert result.status == ResultStatus.FAIL
