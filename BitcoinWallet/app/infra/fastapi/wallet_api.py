from fastapi import APIRouter, Depends

from app.core.facade import WalletService
from app.core.wallet.interactor import (
    CreateWalletRequest,
    GetWalletRequest,
    GetWalletResponse,
)
from app.infra.fastapi.dependables import get_core
from app.utils.result import Result

wallet_api = APIRouter()


@wallet_api.post("/wallets")
def create_new_wallet(
    api_key: str, core: WalletService = Depends(get_core)
) -> Result[GetWalletResponse]:
    return core.create_wallet(request=CreateWalletRequest(api_key=api_key))


@wallet_api.get("/wallets/{address}")
def get_wallet(
    address: int, api_key: str, core: WalletService = Depends(get_core)
) -> Result[GetWalletResponse]:
    return core.get_wallet(
        request=GetWalletRequest(api_key=api_key, wallet_address=address)
    )
