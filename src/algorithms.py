from user import User, DUMMY_USER
from typing import Callable
from functools import reduce
from random import randint, choice


def _snr(user: User) -> int:
    """
    Generates a random instantaneous SNR value for a given user.

    The SNR is randomly selected between 0 and twice the user's
    average SNR.

    Args:
        user: The user for whom the SNR is generated.

    Returns:
        A simulated instantaneous SNR value.
    """
    return randint(0, user.avgSNR * 2)


def max_snr(users: list[User]) -> tuple[User, int]:
    """
    Selects the user with the highest instantaneous SNR.

    Args:
        users: List of candidate users.

    Returns:
        A tuple containing:
            - The selected user with the highest SNR.
            - The corresponding SNR value.

    Notes:
        If the user list is empty, a dummy user with SNR -1
        is returned.
    """

    def _select_max(
        acc: tuple[User, int], user: User
    ) -> tuple[User, int]:
        """
        Compares the current best user (accumulator) with a new user
        and returns the one with the higher SNR.
        """
        snr = _snr(user)
        return acc if acc[1] >= snr else (user, snr)

    return reduce(_select_max, users, (DUMMY_USER, -1))

def rr(users: list[User]) -> tuple[User, int]:
    """
    This implementation is a Random Access strategy, similar in result as RR
    Randomly selects the user.

    Args:
        users: List of candidate users.

    Returns:
        A tuple containing:
            - The randomly selected user.
            - The corresponding SNR value.

    Notes:
        If the user list is empty, a dummy user with SNR -1
        is returned.
    """
    selected = choice(users)
    return (selected, _snr(selected)) if selected is not None else (DUMMY_USER, -1)

#: Dictionary mapping algorithm names to their implementation.
algos: dict[str, Callable[[list[User]], tuple[User, int]]] = {
    "MaxSNR": max_snr,
    "RR": rr
}
