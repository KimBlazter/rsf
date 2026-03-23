import math

from constant import LOIN_AVG_SNR, PROCHE_AVG_SNR
from user import User

def init(n: int):
    users = []
    for i in range(math.floor(n / 2)):
        # Generate the same amount of close and far users
        users.append(User(2 * i, LOIN_AVG_SNR))  # far users
        users.append(User(2 * i + 1, PROCHE_AVG_SNR))  # close users
    return users
