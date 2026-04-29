import math

from constant import HIGH_RELAY_RATIO, LOIN_AVG_SNR, LOW_RELAY_RATIO, PROCHE_AVG_SNR
from user import User
from random import random, shuffle

def init(n: int):
    users = []
    for i in range(math.floor(n / 3)):
        relay_ratio = HIGH_RELAY_RATIO if random() > 0.5 else LOW_RELAY_RATIO 
        # Generate the same amount of close and far users
        new_users = [
            User(3 * i, LOIN_AVG_SNR, relay_ratio),
            User(3 * i + 1, PROCHE_AVG_SNR, relay_ratio),
            User(3 * i + 2, 0, 0)
        ]
        new_users[0].linked_user = new_users[1].linked_user = new_users[2]
        users.extend(new_users)

    return users
