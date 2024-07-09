import time
import random
from typing import Callable
from functools import partial
from multiprocessing import Pool


test_cases = ["dog", "cat", "horse", "fish", "goat", "flower", "basket", "farmhouse", "ocean"]

def take_two(x: str) -> str:
     assert len(x) > 2, f"Input '{x}' must have length greater than 2."
     return "".join([x[idx] for idx in random.sample(range(0, len(x)), k=2)])

def take_three_add_number(x: str) -> str:
    assert len(x) >= 3, f"Input '{x}' must have length greater than 3."
    return "".join([x[idx] for idx in random.sample(range(0, len(x)), k=3)]) + str(random.randint(0, 9))


def _func_with_sleep_time(x, func: Callable, sleep_time: int):
    time.sleep(sleep_time)
    result = func(x)
    print(f"... result of '{result}' from '{x}'")
    return result


def func_pooler(func: Callable, data: list, sleep_time: int | None = None) -> list:
    if sleep_time is not None:
        func = partial(_func_with_sleep_time, func=func, sleep_time=sleep_time)

    with Pool(processes=3) as p:
        results = p.map(func, data)
        p.close()
    return results


def main():

    results = func_pooler(take_three_add_number, test_cases, sleep_time=2)

if __name__ == "__main__":
    main()
