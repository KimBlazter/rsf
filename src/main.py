import argparse
import concurrent.futures
from time import perf_counter
from itertools import repeat

from argparser import parse_users_list, parse_users_mult, parse_users_range
from constant import PACKET_SIZE
from initialization import init
from mesures import (
    finalise_round,
    generate_final_plot,
    generate_plots,
    process_delay,
    record_ur_usage,
)
from packet import PacketGenerator
from scheduler import Scheduler
from user import User
from algorithms import algos

def main(max_ticks: int, nb_users: int | list[int], algorithm: str, measure_time: bool = False):
    if isinstance(nb_users, int):
        simulate(0, max_ticks, nb_users, algorithm, measure_time)
        return

    print(
        f"Running {len(nb_users)} simulations using the {algorithm} algorithm with {max_ticks} max ticks and {nb_users} users..."
    )
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(simulate, range(len(nb_users)), repeat(max_ticks), nb_users, repeat(algorithm)))

    bits_ur_by_user = [bits_entry for bits_entry, _ in results]
    ur_pct_by_user = [ur_entry for _, ur_entry in results]

    generate_final_plot(bits_ur_by_user, ur_pct_by_user)
    print(f"Successfully done {len(nb_users)} simulations!")


def simulate(sim_id: int, max_ticks: int, nb_users: int, algorithm: str, measure_time: bool = False) -> tuple[tuple[float, int], tuple[float, int]]:
    print(f"\tInitializing simulation #{sim_id}")
    start = perf_counter()

    users: list[User] = init(nb_users)

    packet_gen = PacketGenerator(
        1000, PACKET_SIZE
    )  # 1000 bits/tick max, 50 paquet size # Bits/ticks calculé selon notre objectif de crash
    scheduler = Scheduler(algorithm)

    print("\tStarting simulation...")
    tick = 0
    while tick < max_ticks:
        if tick % 500 == 0:
            print(f"(#{sim_id}) Iteration {tick}...")
        packet_gen.generateUsersPackets(
            users, tick
        )  # Generate packets in each user's buffer
        updates: list[tuple[User, int]] = scheduler.select_repartition(
            users
        )  # Donner les UR aux users

        miss = scheduler.apply_repartition(updates, tick)  # Vider les paquets utilisés

        # record UR missrate
        record_ur_usage(scheduler.MAX_UR - miss, scheduler.MAX_UR)

        # record delay
        process_delay(users, tick)

        tick += 1
    end = perf_counter()
    print(f"\tSimulation #{sim_id} successfully ended in {(end - start):0.2f}s !")
    
    generate_plots(sim_id)
    return finalise_round(nb_users)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("max_ticks", type=int, help="Max ticks per simulation")
    parser.add_argument(
        "algo", type=str, help="The algorithm to use.", choices=algos.keys()
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--users", type=int, help="Constant user count across simulations"
    )
    group.add_argument(
        "--users-list", type=parse_users_list, help="User number list (e.g. 2,3,5)"
    )
    group.add_argument(
        "--users-range",
        type=parse_users_range,
        help="User number list range (start:iterations:step)",
    )
    group.add_argument(
        "--users-mult",
        type=parse_users_mult,
        help="User number list mult (start:iterations:multiplier)",
    )
    
    parser.add_argument("--time", action="store_true" ,help="Measure simulations time")

    args = parser.parse_args()

    if args.users is not None:
        main(args.max_ticks, args.users, args.algo, measure_time=args.time)
    else:
        users_list: list[int] = args.users_list or args.users_range or args.users_mult
        main(args.max_ticks, users_list, args.algo, measure_time=args.time)
        
