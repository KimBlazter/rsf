from user import User
from algorithms import algos

BITS_PER_SNR_POINT = 4

class Scheduler():
    MAX_UR = 640 # 128 * 5

    def __init__(self, algorithm: str) -> None:
        self.algorithm = algorithm
        pass
        

    def apply(self, users: list[User])-> list[tuple[User, int]]:
        scheduled = []
        for _ in range(self.MAX_UR):
            best_user, snr = self.chooseUser(users)
            scheduled.append((best_user, snr * BITS_PER_SNR_POINT))
        return scheduled
    
    def chooseUser(self, users: list[User]) -> tuple[User, int] :
        if algos.get(self.algorithm) == None:
            raise Exception("Unknown algorithm")
        return algos.get(self.algorithm)(users) # pyright: ignore[reportOptionalCall]