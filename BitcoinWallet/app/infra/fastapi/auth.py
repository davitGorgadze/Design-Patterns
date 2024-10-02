from fastapi import APIRouter, Depends

from app.core.facade import WalletService
from app.core.auth.interactor import RegisterUserRequest, RegisterUserResponse
from app.infra.fastapi.dependables import get_core
from app.utils.result import Result

auth_api = APIRouter()


@auth_api.post("/users")
def register_user(
    username: str,
    core: WalletService = Depends(get_core),
) -> Result[RegisterUserResponse]:
    return core.register_user(RegisterUserRequest(username))
