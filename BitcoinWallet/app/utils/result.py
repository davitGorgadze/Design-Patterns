import enum
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class ResultStatus(enum.IntEnum):
    SUCCESS = 200
    FAIL = 404
    INTERNAL_ERROR = 500


@dataclass
class Result(Generic[T]):
    status: ResultStatus = ResultStatus.SUCCESS
    data: Optional[T] = None
    exception: Optional[Exception] = None
