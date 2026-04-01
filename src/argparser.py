import argparse

from algorithms import algos


def parse_algo_list(value: str) -> list[str]:
    algo_list = [x.strip() for x in value.split(",")]
    for a in algo_list:
        if a not in algos:
            raise argparse.ArgumentTypeError(
                f"Unknown algorithm: {a}. Choose from {list(algos.keys())}"
            )
    return algo_list


def parse_users_list(value: str) -> list[int]:
    try:
        users = [int(x.strip()) for x in value.split(",")]
    except ValueError as e:
        raise argparse.ArgumentTypeError("--users-list must contain integers separated by ',' ")

    return users

def parse_users_range(value: str) -> list[int]:
    """
    format {start_value}:{iterations}:{step}
    """
    try:
        start_value_s, iterations_s, step_s  = value.split(":")
        start_value = int(start_value_s)
        iterations = int(iterations_s)
        step = int(step_s)
    except ValueError as e:
        raise argparse.ArgumentTypeError("--users-range must be '{start_value}:{iterations}:{step}")

    if start_value <= 0 or iterations <= 0 or step <= 0:
        raise argparse.ArgumentTypeError("start_value, iterations and step should be > 0")
    
    users: list[int] = []
    current: int = start_value
    for _ in range(iterations):
        users.append(current)
        current += step
        
    return users

        
def parse_users_mult(value: str) -> list[int]:
    """
    format {start_value}:{iterations}:{multiplier}
    """
    try:
        start_value_s, iterations_s, multiplier_s  = value.split(":")
        start_value = int(start_value_s)
        iterations = int(iterations_s)
        multiplier = float(multiplier_s)
    except ValueError as e:
        raise argparse.ArgumentTypeError("--users-mult must be '{start_value}:{iterations}:{multiplier}'") from e
    
    if start_value <= 0 or iterations <= 0 or multiplier <= 0:
        raise argparse.ArgumentTypeError("start_value, iterations and multiplier should be > 0")
    
    users: list[int] = []
    current = float(start_value)
    for _ in range(iterations):
        users.append(int(round(current)))
        current *= multiplier
        
    return users