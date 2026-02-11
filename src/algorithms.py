from user import User
from typing import Callable
from functools import reduce
from random import randint

def _SNR(u: User) -> int:
    return randint(0, u.avgSNR*2)

def maxSNR(users: list[User]) -> tuple[User, int]:
    def _maxSNR(acc :tuple[User, int], e: User)-> tuple[User, int]:
        return acc if max(acc[1], _SNR(e)) == acc[1] else (e, _SNR(e))
    dummy = User(-1, -1)
    return reduce(_maxSNR, users, (dummy, -1))

algos: dict[str, Callable[[list[User]], tuple[User, int]]] = {
    "MaxSNR" : maxSNR
}