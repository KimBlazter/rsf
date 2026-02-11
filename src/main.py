from packet import PacketGenerator
from scheduler import Scheduler
from src.initialization import init
import sys

def main(max_ticks: int, nb_users: int, algorithm: str):
    print("Initializing simulation")
    print(f"Simulation duration: {max_ticks} ticks")
    print(f"User number: {nb_users}")
    print(f"Algorithm used: {algorithm}")

    users = init(nb_users)

    packet_gen = PacketGenerator(1000, 100) # 1000 bits/tick max, 100 paquet size # Bits/ticks calculé selon notre objectif de crash
    scheduler = Scheduler(algorithm)

    tick = 0
    print("Starting simulation...")
    while (tick < max_ticks) :
        packet_gen.generateUsersPackets(users, tick) # Generate packets in each user's buffer
        scheduler.apply() # Donner les UR aux users
        apply_scheduling() # Vider les paquets utilisés 
        sample() # Prendre les mesures
        tick += 1

    display_stats()



if __name__ == "__main__":
    if (len(sys.argv) != 3):
        print("Invalid number of arguments.")
        print("Please use ./main.py {MAX_TICKS} {NB_USERS} {ALGO}")
        sys.exit(1)
    
    main(int(sys.argv[0]), int(sys.argv[1]), str(sys.argv[2]))
