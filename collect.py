import os
import requests
from bs4 import BeautifulSoup


# templated path for programme episode listings
FULL_URL = (
    "https://www.bbc.co.uk/programmes/"
    "b006qykl/"
    "episodes/player?"
    "page={page_num}"
)

# number of available pages for enumeration
TOTAL_NUM_PAGES = 104


def main():

    print(FULL_URL.format(page_num="44"))
    return


if __name__ == '__main__':
    main()
