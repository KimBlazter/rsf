import argparse
import concurrent.futures
import os
import shutil
from functools import reduce
from time import perf_counter

from argparser import (
    parse_algo_list,
    parse_users_list,
    parse_users_mult,
    parse_users_range,
)
from constant import PACKET_SIZE
from initialization import init
from mesures import (
    OUTPUT_DIR,
    finalise_round,
    generate_combined_plot,
    generate_final_plot,
    generate_plots,
    process_delay,
    record_ur_usage,
)
from packet import PacketGenerator
from scheduler import Scheduler
from user import DUMMY_USER, User


def main(
    max_ticks: int,
    nb_users: int | list[int],
    algorithms: list[str],
    measure_time: bool = False,
) -> None:
    if isinstance(nb_users, int):
        nb_users_list = [nb_users]
        single_user = True
    else:
        nb_users_list = nb_users
        single_user = False

    if len(algorithms) == 1 and single_user:
        _ = simulate(0, max_ticks, nb_users_list[0], algorithms[0], measure_time)
        return

    start = perf_counter() if measure_time else 0

    tasks = [(algo, i, n) for algo in algorithms for i, n in enumerate(nb_users_list)]

    print(
        f"Running {len(tasks)} simulations with algorithms {algorithms}, {max_ticks} max ticks and {nb_users_list} users..."
    )
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(simulate, i, max_ticks, n, algo, measure_time): (algo, i)
            for algo, i, n in tasks
        }
        results_by_algo: dict[str, list] = {  # pyright: ignore[reportMissingTypeArgument]
            algo: [None] * len(nb_users_list) for algo in algorithms
        }
        for done_count, f in enumerate(concurrent.futures.as_completed(futures), 1):
            algo, idx = futures[f]
            results_by_algo[algo][idx] = f.result()
            print(
                f"Progress: {done_count}/{len(tasks)} ({done_count * 100 // len(tasks)}%)"
            )

    if not single_user:
        for algo in algorithms:
            results = results_by_algo[algo]
            bits_ur_by_user = [r[0] for r in results if r is not None]
            ur_pct_by_user = [r[1] for r in results if r is not None]
            delai_proche_by_user = [r[2] for r in results if r is not None]
            delai_loin_by_user = [r[3] for r in results if r is not None]
            generate_final_plot(
                bits_ur_by_user,
                ur_pct_by_user,
                delai_proche_by_user,
                delai_loin_by_user,
                algo,
            )
        if len(algorithms) > 1:
            generate_combined_plot(results_by_algo)

    print(
        f"Successfully done {len(tasks)} simulations{f' in {perf_counter() - start:.2f}s' if measure_time else ''} !"
    )


def simulate(
    sim_id: int,
    max_ticks: int,
    nb_users: int,
    algorithm: str,
    measure_time: bool = False,
) -> tuple[tuple[float, int], tuple[float, int], tuple[float, int], tuple[float, int]]:
    print(f"\tInitializing simulation #{sim_id}")
    start = perf_counter() if measure_time else 0

    users: list[User] = init(nb_users)

    packet_gen = PacketGenerator(
        10000, PACKET_SIZE
    )  # 10000 bits/tick max, 50 paquet size # Bits/ticks calculé selon notre objectif de crash
    scheduler = Scheduler(algorithm)

    print("\tStarting simulation...")
    tick = 0
    while tick < max_ticks:
        if tick % 500 == 0:
            print(f"(#{sim_id}) Iteration {tick}...")
        _ = packet_gen.generateUsersPackets(
            users, tick
        )  # Generate packets in each user's buffer
        updates: list[tuple[User, int]] = scheduler.select_repartition(
            users, tick
        )  # Donner les UR aux users

        # compute number of unsued UR 
        miss = sum(1 for user, bits in updates if user is DUMMY_USER or bits == -1)
        # print(f"dummmy : {DUMMY_USER}")
        # print(f"list: {updates}")

        # record UR missrate
        _ = record_ur_usage(scheduler.MAX_UR - miss, scheduler.MAX_UR)

        # record delay
        _ = process_delay(users, tick)

        tick += 1
    end = perf_counter() if measure_time else 0
    if measure_time:
        print(f"\tSimulation #{sim_id} successfully ended in {(end - start):0.2f}s !")
    else:
        print(f"\tSimulation #{sim_id} successfully ended !")

    _ = generate_plots(sim_id, algorithm)
    return finalise_round(nb_users)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("max_ticks", type=int, help="Max ticks per simulation")
    parser.add_argument(
        "algo",
        type=parse_algo_list,
        help="Algorithm(s) to use, comma-separated (e.g. MaxSNR,RR,CEI)",
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

    parser.add_argument("--time", action="store_true", help="Measure simulations time")

    args = parser.parse_args()

    # Clear measurements output dir
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR)
        print(f"Cleared {OUTPUT_DIR} directory")
    else:
        os.makedirs(OUTPUT_DIR)
        print(f"Created {OUTPUT_DIR} directory")

    algorithms: list[str] = args.algo

    if args.users is not None:
        main(args.max_ticks, args.users, algorithms, measure_time=args.time)
    else:
        users_list: list[int] = args.users_list or args.users_range or args.users_mult
        main(args.max_ticks, users_list, algorithms, measure_time=args.time)
