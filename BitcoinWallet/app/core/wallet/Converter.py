import ast
from typing import Protocol

import requests


class IConverter(Protocol):
    def get_BTC_to_USD_conversion_rate(self) -> float:
        pass


class WrongConverter:
    def __init__(self) -> None:
        self.conversion = 1

    def get_BTC_to_USD_conversion_rate(self) -> float:
        return self.conversion


class GeneralBTCConversionDataRetriever:
    def __init__(self, url: str = "https://blockchain.info/ticker") -> None:
        self.url = url

    def fetch_data(self) -> dict:
        response = requests.get(self.url)
        bytes_str = response.content
        dict_str = bytes_str.decode("UTF-8")
        data_dict = ast.literal_eval(dict_str)
        return data_dict


class APIConverter(GeneralBTCConversionDataRetriever):
    def __init__(self, url: str = "https://blockchain.info/ticker") -> None:
        super().__init__(url)
        self.symbol = "USD"

    def get_BTC_to_USD_conversion_rate(self) -> float:
        return self.fetch_data()[self.symbol]["last"]
