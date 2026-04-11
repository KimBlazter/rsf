from functools import reduce

import constant
from algorithms import algos
from user import DUMMY_USER, User


class Scheduler:
    """
    Schedules users according to a selected algorithm and distributes
    radio resources (UR) based on their SNR.

    Attributes:
        MAX_UR: Maximum number of scheduling units per repartition cycle.
        algorithm: Name of the scheduling algorithm to use.
    """

    MAX_UR = constant.MAX_UR

    def __init__(self, algorithm: str) -> None:
        """
        Initializes the scheduler with a given scheduling algorithm.

        Args:
            algorithm: Name of the algorithm used to select users.
        """
        self.algorithm = algorithm
        pass

    def select_repartition(
        self, users: list[User], curr_tick: int
    ) -> list[tuple[User, int]]:
        """
        Selects users repeatedly until MAX_UR is reached and computes
        the bit allocation for each selected user.

        Args:
            users: List of active users eligible for scheduling.

        Returns:
            List of tuples containing:
                - The selected user.
                - The number of allocated bits.
        """
        selected_users = [u for u in users if u.buffer.current_size > 0]
        scheduled = []

        for _ in range(self.MAX_UR):
            best_user, snr = self.select_user(selected_users, curr_tick)
            bits_to_allocate = snr * constant.BITS_PER_SNR_POINT
            scheduled.append((best_user, bits_to_allocate))

            if best_user is DUMMY_USER:
                continue

            best_user.allocate_bits(bits_to_allocate, curr_tick, self.algorithm)

            # print(f"SIZE: {reduce(lambda acc, u: acc + u.buffer.current_size, selected_users, 0)}, SNR: {snr}")
            if best_user.buffer.current_size <= 0:
                selected_users.remove(best_user)

        return scheduled

    def apply_repartition(
        self, repartition: list[tuple[User, int]], curr_tick: int
    ) -> int:
        """
        Applies the computed repartition by delivering the allocated
        bits to each scheduled user.

        Args:
            repartition: List of tuples containing users and their
                        corresponding allocated bits.
        """
        # self.print_loin_users_allocation(repartition) # REMOVE
        miss = 0
        for user, bits in repartition:
            if user is DUMMY_USER or bits == -1:
                miss += 1
                continue
            user.allocate_bits(bits, curr_tick, self.algorithm)  # give bits to user
        return miss

    def select_user(self, users: list[User], tick: int) -> tuple[User, int]:
        """
        Selects a single user according to the configured scheduling
        algorithm.

        Args:
            users: List of active users eligible for scheduling.

        Returns:
            A tuple containing:
                - The selected user.
                - The associated SNR value.

        Raises:
            Exception: If the configured algorithm is unknown.
        """
        if algos.get(self.algorithm) == None:
            raise Exception("Unknown algorithm")
        return algos.get(self.algorithm)(users, tick)  # pyright: ignore[reportOptionalCall]
