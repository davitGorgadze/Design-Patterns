from fastapi import APIRouter, Depends

from app.core.facade import WalletService
from app.core.statistics.interactor import StatisticsRequest, StatisticsResponse
from app.infra.fastapi.dependables import get_core
from app.utils.result import Result

statistics_api = APIRouter()


@statistics_api.get("/statistics")
def get_statistics(
    user_key: str, core: WalletService = Depends(get_core)
) -> Result[StatisticsResponse]:
    return core.get_statistics(request=StatisticsRequest(user_key=user_key))
