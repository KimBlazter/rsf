import math

def init(n: int):
    users = []
    for i in range(math.floor(n/2)):
        # Generate the same amount of close and far users
        users.append(User())
    return users