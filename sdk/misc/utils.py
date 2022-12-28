import json
import functools
from timeit import default_timer as timer
from typing import Dict, Callable, Iterable
from loguru import logger
from datetime import datetime
import concurrent.futures
import os


def normalize_symbol(symbol: str) -> str:
    symbol = symbol.replace(" ", "")
    if len(symbol) > 5 or not symbol:
        raise ValueError(f"Symbol '{symbol}' must be between 1 and 5 letters long.")
    return symbol.upper()


def currency(val: float) -> str:
    return f"${val:,.2f}"


def save_cfg(config: Dict, cfg_file: str = "../config.json"):
    with open(cfg_file, "w") as cfg:
        json.dump(config, cfg)
    logger.debug(f"UPDATED {cfg_file}")


def load_cfg(prepend_path: str) -> Dict:
    cfg_file = os.path.join(prepend_path, "config.json")
    with open(cfg_file, "r") as cfg:
        return json.load(cfg)


def format_datetime_12h(time: datetime) -> str:
    time = time.strftime("%Y-%m-%d %I:%M %p")
    return time


def timed(func):
    """(decorator) Logs the runtime of decorated method."""

    @functools.wraps(func)
    def wrapper_timed(*args, **kwargs):
        start = timer()
        logger.debug(
            f"Starting function {func.__name__}"
            f"({args if args else kwargs if kwargs else None})..."
        )
        value = func(*args, **kwargs)
        end = timer()
        seconds_elapsed = round(end - start, 2)
        logger.success(
            f"Function {func.__name__}"
            f"({args if args else kwargs if kwargs else None}) executed in {seconds_elapsed} seconds."
        )
        return value

    return wrapper_timed


def debug(func):
    """(decorator) Print the function signature and return value"""

    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(arg) for arg in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        logger.debug(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        logger.debug(f"{func.__name__!r} returned {value!r}")
        return value

    return wrapper_debug


def use_threadpool_exec(func: Callable, iterable: Iterable) -> Iterable:
    """
    Use threading to improve performance for vast amounts of repetitive operations.
    func param will be passed to a map function - use functools.partial(func, **kwargs) if args are required before
    passing in func to use_threadpool_exec.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        data = executor.map(func, iterable)
    return list(data)


if __name__ == "__main__":
    pass
    # config = {
    #     "BASE_DB_PATH": "../databases/sqlite.db",
    #     "BASE_DB_PATH_DUMMY": "../databases/sqlite_dummy.db",
    #     "TICKER_DATA_PATH": "../ticker_data/",
    #     "PORTFOLIO_DATA_PATH": "../portfolio_data/"
    # }
    # save_cfg(config)
    # now = datetime.now()
    # print(format_datetime_12h(now))
    # from time import sleep
    #
    # @timed
    # def test():
    #     for i in range(0, 100):
    #         sleep(0.01)
    #
    # test()
