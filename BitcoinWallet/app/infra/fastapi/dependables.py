from starlette.requests import Request

from app.core.facade import WalletService


def get_core(request: Request) -> WalletService:
    return request.app.state.core
