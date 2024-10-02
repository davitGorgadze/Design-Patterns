import random
from _testcapi import INT_MAX
from abc import ABC, abstractmethod


class IApiKeyGenerator(ABC):
    @abstractmethod
    def generate_key(self, username: str) -> str:
        pass


class DummyApiKeyGenerator(IApiKeyGenerator):
    def generate_key(self, username: str) -> str:
        return username + str(random.randint(1000, INT_MAX))
