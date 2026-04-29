from functools import reduce
from random import choice, randint
from typing import Callable

from user import DUMMY_USER, User
from constant import WF_ALPHA, WF_BETA


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


def max_snr(users: list[User], tick: int) -> tuple[User, int]:
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

    def _select_max(acc: tuple[User, int], user: User) -> tuple[User, int]:
        """
        Compares the current best user (accumulator) with a new user
        and returns the one with the higher SNR.
        """
        snr = _snr(user)
        return acc if acc[1] >= snr else (user, snr)

    return reduce(_select_max, users, (DUMMY_USER, -1))


def rr(users: list[User], tick: int) -> tuple[User, int]:
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
    if users == []:
        return (DUMMY_USER, -1)
    selected = choice(users)
    return (selected, _snr(selected)) if selected is not None else (DUMMY_USER, -1)


def cei(users: list[User], tick: int) -> tuple[User, int]:
    """
    Selects the user with the highest vaul of (SNR * RELAY_RATIO)

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

    def _select_max(acc: tuple[User, int, int], user: User) -> tuple[User, int, int]:
        """
        Compares the current best user (accumulator) with a new user
        and returns the one with the higher SNR.
        """
        snr = _snr(user)
        metric = snr * (user.relay_ratio + 0.1) # ratio can be 0
        return acc if acc[1] >= snr else (user, metric, snr)

    if users == []:
        return (DUMMY_USER, -1)

    best_user, _, snr = reduce(_select_max, users, (DUMMY_USER, -1, -1))
    return (best_user, snr)
    

def pf(users: list[User], tick: int) -> tuple[User, int]:
    
    def _select_max(acc: tuple[User, int, int], user: User) -> tuple[User, int, int]:
        # user snr / user avg snr
        snr = _snr(user)
        snr_on_avg_snr = int(snr / user.avgSNR)
        return acc if acc[1] >= snr_on_avg_snr else (user, snr_on_avg_snr, snr)

    best_user, _, snr = reduce(_select_max, users, (DUMMY_USER, -1,-1))
    return (best_user, snr)


def wfo(users: list[User], tick: int) -> tuple[User, int]:
    """
    Selects the user with the highest WFO score: SNR * WF_k(tick).

    Args:
        users: List of candidate users.
        tick: Current simulation tick.

    Returns:
        A tuple containing:
            - The selected user.
            - The selected user's capacity for this RU.

    Notes:
        If the user list is empty, a dummy user with score and SNR set to -1
        is returned.
        WF_k(tick) is calculated as: 1 + WF_BETA * PDOR_k(tick)^WF_ALPHA
    """
    def _select_max(acc: tuple[User, float, int], user: User) -> tuple[User, float, int]:
        """
        Compares the current best user (accumulator) with a new user
        and returns the one with the higher WFO score.
        """
        snr = _snr(user)
        wf = 1 + WF_BETA * (user.get_pdor(tick) ** WF_ALPHA)
        wfo = snr * wf
        return acc if acc[1] >= wfo else (user, wfo, snr)  # Keep current best when scores tie.

    best_user, _, snr = reduce(_select_max, users, (DUMMY_USER, -1, -1))
    return (best_user, snr)  # Scheduler consumes SNR as RU capacity proxy.

def cei_wfo(users: list[User], tick: int) -> tuple[User, int]:
    def _select_max(acc: tuple[User, float, int], user: User) -> tuple[User, float, int]:
        snr = _snr(user)
        wf = 1 + WF_BETA * (user.get_pdor(tick) ** WF_ALPHA)
        score = snr * (user.relay_ratio + 0.1) * wf
        return acc if acc[1] >= score else (user, score, snr)  # Keep current best when scores tie.

    best_user, _, snr = reduce(_select_max, users, (DUMMY_USER, -1, -1))
    return (best_user, snr)

#: Dictionary mapping algorithm names to their implementation.
algos: dict[str, Callable[[list[User], int], tuple[User, int]]] = {
    "MaxSNR": max_snr,
    "RR": rr,
    "CEI": cei,
    "WFO": wfo,
    "PF": pf,
}
