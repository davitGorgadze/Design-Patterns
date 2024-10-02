from dataclasses import dataclass, field
from typing import Optional

from app.core.exceptions import WalletRequestError
from app.core.wallet.Converter import APIConverter, IConverter
from app.core.wallet.wallet import IWallet, IWalletRepository
from app.utils.result import Result, ResultStatus


@dataclass
class GetWalletRequest:
    api_key: str
    wallet_address: int


@dataclass
class CreateWalletRequest:
    api_key: str


@dataclass
class GetWalletResponse:
    wallet_address: int
    amount_BTC: float
    amount_USD: float


@dataclass
class WalletInteractor:
    wallet_repository: IWalletRepository
    converter: IConverter = field(default_factory=APIConverter)

    def create_new_wallet(
        self, request: CreateWalletRequest
    ) -> Result[GetWalletResponse]:
        wallet, error_str = self.wallet_repository.create_wallet(request.api_key)
        return self._create_response(wallet, error_str)

    def get_wallet(self, request: GetWalletRequest) -> Result[GetWalletResponse]:
        wallet, error_str = self.wallet_repository.get_wallet(
            api_key=request.api_key, address=request.wallet_address
        )
        return self._create_response(wallet, error_str)

    def _create_response(
        self, wallet: Optional[IWallet], error_str: Optional[str]
    ) -> Result[GetWalletResponse]:
        if wallet is None and error_str is not None:
            return Result(
                status=ResultStatus.FAIL,
                data=None,
                exception=WalletRequestError(message=error_str),
            )
        else:
            conversion_rate = self.converter.get_BTC_to_USD_conversion_rate()
            if conversion_rate is None:
                return Result(
                    status=ResultStatus.INTERNAL_ERROR,
                    data=None,
                    exception=WalletRequestError(message="Internal Server Error"),
                )

            amount_in_btc = wallet.get_amount()
            amount_in_usd = amount_in_btc * conversion_rate
            return Result(
                status=ResultStatus.SUCCESS,
                data=GetWalletResponse(
                    wallet_address=wallet.get_address(),
                    amount_BTC=amount_in_btc,
                    amount_USD=amount_in_usd,
                ),
            )
