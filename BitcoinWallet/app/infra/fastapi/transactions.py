from fastapi import APIRouter, Depends

from app.core.facade import WalletService
from app.core.transaction.interactor import (
    MakeTransactionRequest,
    MakeTransactionResponse,
    UserTransactionsRequest,
    UserTransactionsResponse,
    WalletTransactionsRequest,
    WalletTransactionsResponse,
)
from app.infra.fastapi.dependables import get_core
from app.utils.result import Result

transactions_api = APIRouter()


@transactions_api.post("/transactions")
def make_transaction(
    api_key: str,
    from_wallet_address: int,
    to_wallet_address: int,
    balance: float,
    core: WalletService = Depends(get_core),
) -> Result[MakeTransactionResponse]:
    return core.make_transaction(
        MakeTransactionRequest(api_key, from_wallet_address, to_wallet_address, balance)
    )


@transactions_api.get("/transactions")
def get_transactions(
    api_key: str, core: WalletService = Depends(get_core)
) -> Result[UserTransactionsResponse]:
    return core.get_user_transactions(UserTransactionsRequest(api_key))


@transactions_api.get("/wallets/{address}/transactions")
def get_wallet_transactions(
    api_key: str, address: int, core: WalletService = Depends(get_core)
) -> Result[WalletTransactionsResponse]:
    return core.get_wallet_transactions(WalletTransactionsRequest(api_key, address))
