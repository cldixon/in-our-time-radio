import os
import re
import random
from enum import StrEnum
from datetime import datetime

import requests
import polars as pl
from bs4 import BeautifulSoup

from programme import extract_programme_data_from_html

# set output values
DATA_DIR = "data"


# templated path for programme episode listings
FULL_URL = (
    "https://www.bbc.co.uk/programmes/"
    "b006qykl/"                          # <- id for 'In Our Time'
    "episodes/player?"
    "page={page_num}"                    # <- template for specifying page number
)

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
}

## -- UTILITIES ----
def get_timestamp() -> str:
    return datetime.now().isoformat(sep=" ", timespec="milliseconds")


def get_html(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(resp.content, features="lxml")
    return soup


class MaxAvailablePageTag(StrEnum):
    TAG_TYPE = "li"
    CLASS_NAME = "pagination__page--last"


def get_max_available_page(soup: BeautifulSoup) -> int:
    max_available_page = soup.find(MaxAvailablePageTag.TAG_TYPE, MaxAvailablePageTag.CLASS_NAME)
    if max_available_page is not None:
        max_page_num = max_available_page.get_text(strip=True)
    else:
        raise ValueError(f"{MaxAvailablePageTag.TAG_TYPE} tag with class '{MaxAvailablePageTag.CLASS_NAME}' not found. This is used to identify the maximum available page number.")

    try:
        return int(max_page_num)
    except:
        raise ValueError(f"Extracted '{max_page_num}', but this value could not be converted to an integer.")

def extract_programme_page_urls(html_content: BeautifulSoup) -> list[str]:
    programmes_listing = html_content.find_all("div", {"class": "programme"})
    return [
        programme.find("h2", {"class": "programme__titles"}).find("a").get("href")
        for programme in programmes_listing
    ]







def main():

    ## -- STAGE 1: COLLECT ALL PROGRAMME URLS ----
    print(f"# -- Programme Archive Bulk Collection ----")

    # get available page numbers
    # check on random page
    random_page_num = random.randint(10, 85)
    listing_page = FULL_URL.format(page_num=random_page_num)
    html_content = get_html(listing_page)
    max_available_page_num = get_max_available_page(html_content)
    print(f"# -- identifed {max_available_page_num} available pages")


    # create array of page numbers and shuffle
    available_page_numbers = list(range(1, (max_available_page_num + 1)))
    random.shuffle(available_page_numbers)
    programme_listing_page_urls = [
        FULL_URL.format(page_num=page_num)
        for page_num in available_page_numbers
    ]

    # iterate over webpages with article listing, collect urls
    all_programme_urls = []

    for page_url in programme_listing_page_urls[:3]:

        html_content = get_html(page_url)

        # extract all program links
        programme_page_urls = extract_programme_page_urls(html_content)
        print(f"| -> extracted {len(programme_page_urls)} urls from '{page_url}'.")

        all_programme_urls.append(
            pl.DataFrame(
                {
                    "programme_url": programme_page_urls,
                    "listing_page": page_url,
                    "collected": get_timestamp()
                }
            )
        )

    # convert extracted urls to dataframe and save to disk
    extracted_urls = (
        pl.concat(all_programme_urls)
        .sort(by="listing_page")
    )
    extracted_urls.write_csv(os.path.join(DATA_DIR, "programme_urls.csv"))

    ## -- STAGE 2: SCRAPE PROGRAMME CONTENT ----
    all_programme_data = []
    for programme in extracted_urls.sample(fraction=1).to_dicts()[:3]:
        programme_html = get_html(programme["programme_url"])
        programme_data = extract_programme_data_from_html(programme_html)

        print(f"| -> extracted data from '{programme["programme_url"]}':")
        print(f"| ---> {programme_data}")
        print('-' * 35, '\n')
        all_programme_data.append(programme_data)

    return


if __name__ == '__main__':
    main()
