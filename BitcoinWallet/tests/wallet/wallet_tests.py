from app.core.wallet.wallet import BitcoinWallet


def test_initialization():
    wallet1 = BitcoinWallet(wallet_address=0, amount_BTC=0, user_id=0)
    assert wallet1.wallet_address == 0
    assert wallet1.amount_BTC == 0
    assert wallet1.user_id == 0

    wallet2 = BitcoinWallet(wallet_address=42, amount_BTC=3, user_id=23)
    assert wallet2.wallet_address == 42
    assert wallet2.amount_BTC == 3
    assert wallet2.user_id == 23


def test_deposit1():
    wallet = BitcoinWallet(wallet_address=0, amount_BTC=1, user_id=2)
    assert wallet.get_amount() == 1

    wallet.deposit(2)

    assert wallet.get_amount() == 3


def test_deposit2():
    wallet = BitcoinWallet(wallet_address=0, amount_BTC=5, user_id=2)
    assert wallet.get_amount() == 5

    wallet.deposit(5)

    assert wallet.get_amount() == 10


def test_withdraw1():
    wallet = BitcoinWallet(wallet_address=0, amount_BTC=5, user_id=2)
    assert wallet.get_amount() == 5

    wallet.withdraw(3)
    assert wallet.get_amount() == 2


def test_withdraw2():
    wallet = BitcoinWallet(wallet_address=0, amount_BTC=10, user_id=2)
    assert wallet.get_amount() == 10

    wallet.withdraw(6)
    assert wallet.get_amount() == 4


def test_get_address1():
    wallet = BitcoinWallet(wallet_address=1234, amount_BTC=10, user_id=2)
    assert wallet.get_address() == 1234


def test_get_address2():
    wallet = BitcoinWallet(wallet_address=2341, amount_BTC=10, user_id=2)
    assert wallet.get_address() == 2341


def test_set_address():
    wallet = BitcoinWallet(wallet_address=12, amount_BTC=10, user_id=2)
    assert wallet.get_address() == 12

    wallet.set_address(3213)
    assert wallet.get_address() == 3213


def test_get_user():
    wallet1 = BitcoinWallet(wallet_address=1, amount_BTC=2, user_id=5)
    wallet2 = BitcoinWallet(wallet_address=2, amount_BTC=3, user_id=6)

    assert wallet1.get_user() == 5
    assert wallet2.get_user() == 6



