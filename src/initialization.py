import math

from constant import HIGH_RELAY_RATIO, LOIN_AVG_SNR, LOW_RELAY_RATIO, PROCHE_AVG_SNR
from user import User
from random import random, shuffle

def init(n: int):
    users = []
    for i in range(math.floor(n / 2)):
        relay_ratio = HIGH_RELAY_RATIO if random() > 0.5 else LOW_RELAY_RATIO 
        # Generate the same amount of close and far users
        users.append(User(2 * i, LOIN_AVG_SNR, relay_ratio))  # far users
        users.append(User(2 * i + 1, PROCHE_AVG_SNR, relay_ratio))  # close users

    shuffle(users)
    for i in range(math.floor(len(users)/2)):
        users[i].linked_user = users[len(users) - i - 1]
        users[len(users) - i - 1].linked_user = users[i].linked_user
    return users
