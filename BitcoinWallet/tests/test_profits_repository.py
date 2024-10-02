from unittest import TestCase
import random

from app.infra.in_memory.profits_in_memory_repository import ProfitsInMemoryRepository
from app.infra.sql_base.profits_sql_repository import ProfitsRepository


class TestProfitsInMemoryRepository(TestCase):
    def test_all_random(self):
        repo: ProfitsInMemoryRepository = ProfitsInMemoryRepository()
        total_profit: float = .0

        for i in range(random.randint(10, 50)):
            num: float = random.random()
            res = repo.add_system_profit(1, num)
            total_profit += num

            assert res.data == i + 1

        assert total_profit == repo.get_total_profit().data


class TestProfitsRepository(TestCase):
    def test_all_random(self):
        repo: ProfitsRepository = ProfitsRepository(":memory:")
        total_profit: float = .0

        for i in range(random.randint(10, 50)):
            num: float = random.random()
            res = repo.add_system_profit(1, num)
            total_profit += num

            assert res.data == i + 1

        assert total_profit == repo.get_total_profit().data
