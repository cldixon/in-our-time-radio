import time
from typing import Any, Callable
from functools import partial
from datetime import datetime
from multiprocessing import Pool

import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
}


def get_html(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(resp.content, features="lxml")
    return soup


def crawl_func_with_sleep_time(url: str, func: Callable, sleep_time: int):
    time.sleep(sleep_time)
    print(f"| crawling '{url}'")
    try:
        return func(url)
    except Exception as e:
        print(f"Encountered the following error for url '{url}'...")
        raise Exception(e)



def crawl_pooler(crawl_func: Callable, target_urls: list[str], processes: int = 4, sleep_time: int | None = None) -> list:
    assert isinstance(processes, int), f"Input '{processes}' for argument `processes` must be type int. Instead got type '{type(processes)}'."

    # if sleep time is provided create a partial function
    if sleep_time is not None:
        assert isinstance(sleep_time, int), f"Input for argument `sleep_time` must be either `None` or type Int. Instead got type '{type(sleep_time)}' for input '{sleep_time}'."
        crawl_func = partial(crawl_func_with_sleep_time, func=crawl_func, sleep_time=sleep_time)

    with Pool(processes) as p:
        crawl_results = p.map(crawl_func, target_urls)
        p.close()
    return crawl_results


## -- UTILITIES ----
def get_timestamp() -> str:
    return datetime.now().isoformat(sep=" ", timespec="milliseconds")
