import math
from user import User

def init(n: int):
    users = []
    for i in range(math.floor(n/2)):
        # Generate the same amount of close and far users
        users.append(User(2*i, 7)) # far users
        users.append(User(2*i+1, 11)) # close users
    return users