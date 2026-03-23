from functools import reduce
import argparse
from argparser import parse_users_list, parse_users_mult, parse_users_range

from initialization import init
from mesures import finalise_round, record_ur_usage, generate_plots, generate_final_plot
from packet import PacketGenerator
from scheduler import Scheduler
from user import DUMMY_USER, User

def main(max_ticks: int, nb_users: int | list[int], algorithm: str, num_simulations: int = 1):
    if isinstance(nb_users, list) and num_simulations != len(nb_users):
        raise Exception("Simulation number should match user numbers")
        
    print(f"Running {num_simulations} simulations using the {algorithm} algorithm with {max_ticks} max ticks and {nb_users} users...")
    for sim_id in range(num_simulations):
        print("\r")
        nb_usr: int = nb_users[sim_id] if isinstance(nb_users, list) else nb_users
        simulate(sim_id, max_ticks, nb_usr, algorithm)
        finalise_round(nb_usr)
        
    generate_final_plot()
    print(f"Successfully done {num_simulations} simulations!")
    

def simulate(sim_id: int, max_ticks: int, nb_users: int, algorithm: str) -> None:
    print(f"\tInitializing simulation #{sim_id}")

    users: list[User] = init(nb_users)

    packet_gen = PacketGenerator(
        1000, 50
    )  # 1000 bits/tick max, 100 paquet size # Bits/ticks calculé selon notre objectif de crash
    scheduler = Scheduler(algorithm)

    print("\tStarting simulation...")
    tick = 0
    while tick < max_ticks:
        packet_gen.generateUsersPackets(
            users, tick
        )  # Generate packets in each user's buffer
        updates: list[tuple[User, int]] = scheduler.select_repartition(
            users
        )  # Donner les UR aux users

        scheduler.apply_repartition(updates, tick) # Vider les paquets utilisés
        
        # record mesures
        nb_used_ur = reduce(lambda acc, e: (acc+1) if e[0] != DUMMY_USER else acc, updates, 0)
        record_ur_usage(nb_used_ur, len(updates))
        tick += 1
    print(f"\tSimulation #{sim_id} successfully ended !")
    generate_plots(sim_id)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("max_ticks", type=int, help="Max ticks per simulation")
    parser.add_argument("algo", type=str, help="The algorithm to use. (RR, MaxSNR)")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--users", type=int, help="Constant user count across simulations")
    group.add_argument("--users-list", type=parse_users_list, help="User number list (e.g. 2,3,5)")
    group.add_argument("--users-range", type=parse_users_mult, help="User number list range (start:iterations:step)")
    group.add_argument("--users-mult", type=parse_users_range, help="User number list mult (start:iterations:multiplier)")
    
    parser.add_argument("--runs", type=int, help="Number of simulations to run")
    
    args = parser.parse_args()
    
    if args.users is not None:
        main(args.max_ticks, args.users, args.algo, args.runs)
    else:
        users_list = args.users_list or args.users_range or args.users_mult
        main(args.max_ticks, users_list, args.algo, args.runs)
        
