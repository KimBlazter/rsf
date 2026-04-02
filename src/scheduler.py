import constant 
from user import User, DUMMY_USER
from algorithms import algos



class Scheduler():
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
        

    def select_repartition(self, users: list[User]) -> list[tuple[User, int]]:
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
        selected_users = [u for u in users if len(u.buffer.queue) > 0]
        scheduled = []
        for _ in range(min(self.MAX_UR, len(selected_users))):
            best_user, snr = self.select_user(selected_users)
            if (len(best_user.buffer.queue) - snr * constant.BITS_PER_SNR_POINT) < constant.PACKET_SIZE: # remove user if they don't have anything remaning
                selected_users.remove(best_user)
            
            scheduled.append((best_user, snr * constant.BITS_PER_SNR_POINT))

        for _ in range(self.MAX_UR - len(selected_users)):
            scheduled.append((DUMMY_USER, -1))
        return scheduled
    
    def apply_repartition(self, repartition: list[tuple[User, int]], curr_tick: int) -> int:
        """
        Applies the computed repartition by delivering the allocated
        bits to each scheduled user.

        Args:
            repartition: List of tuples containing users and their
                        corresponding allocated bits.
        """
        self.print_loin_users_allocation(repartition)
        miss = 0
        for user, bits in repartition:
            if user is DUMMY_USER or bits == -1:
                miss += 1
                continue
            user.allocate_bits(bits, curr_tick) # give bits to user
        return miss

    def select_user(self, users: list[User]) -> tuple[User, int] :
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
        return algos.get(self.algorithm)(users) # pyright: ignore[reportOptionalCall]

    def print_loin_users_allocation(self, repartition: list[tuple[User, int]]) -> None:
        """
        Simplifies and prints the repartition list to show only users with
        avgSNR == LOIN_AVG_SNR, with their total allocated bits summed.

        Args:
            repartition: List of tuples containing users and their allocated bits.
        """
        # Filter users with LOIN_AVG_SNR and aggregate allocations
        user_allocations = {}
        for user, bits in repartition:
            if user.avgSNR == constant.LOIN_AVG_SNR:
                if user.id not in user_allocations:
                    user_allocations[user.id] = {"user": user, "total_bits": 0}
                user_allocations[user.id]["total_bits"] += bits
        
        # Print the simplified repartition
        print(f"\nUsers with avgSNR == {constant.LOIN_AVG_SNR}:")
        for user_id, data in user_allocations.items():
            user = data["user"]
            total_bits = data["total_bits"]
            print(f"  User {user.id} (avgSNR={user.avgSNR}): {total_bits} bits allocated")