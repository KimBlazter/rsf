from functools import reduce
import sys

from initialization import init
from mesures import record_ur_usage, generate_plots
from packet import PacketGenerator
from scheduler import Scheduler
from user import DUMMY_USER, User

def main(max_ticks: int, nb_users: int, algorithm: str):

    print("Initializing simulation")
    print(f"Simulation duration: {max_ticks} ticks")
    print(f"User number: {nb_users}")
    print(f"Algorithm used: {algorithm}")

    users: list[User] = init(nb_users)

    packet_gen = PacketGenerator(
        1000, 50
    )  # 1000 bits/tick max, 100 paquet size # Bits/ticks calculé selon notre objectif de crash
    scheduler = Scheduler(algorithm)

    print("Starting simulation...")
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
    print("Simulation successfully ended !")
    generate_plots(0)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(sys.argv)
        print("Invalid number of arguments.")
        print("Please use ./main.py {MAX_TICKS} {NB_USERS} {ALGO}")
        sys.exit(1)

    main(int(sys.argv[1]), int(sys.argv[2]), str(sys.argv[3]))
