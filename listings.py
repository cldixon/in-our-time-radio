import os
import time
import random
import argparse
from enum import StrEnum

import polars as pl
from bs4 import BeautifulSoup

from utils import get_soup_from_url, crawl_pooler

parser = argparse.ArgumentParser()

parser.add_argument("--test", action='store_true', help="Flag for testing of script. Will only crawl small number of listing pages.")


args = parser.parse_args()

# data directory
DATA_DIR = "data"
PROGRAMME_URLS_CSV = os.path.join(DATA_DIR, "programme_urls.csv")

# templated path for programme episode listings
PROGRAMME_LISTING_URL_TEMPLATE = (
    "https://www.bbc.co.uk/programmes/"
    "b006qykl/"                          # <- id for 'In Our Time'
    "episodes/player?"
    "page={page_num}"                    # <- template for specifying page number
)

def format_listing_url(page_num: int, url_template: str = PROGRAMME_LISTING_URL_TEMPLATE) -> str:
    return url_template.format(page_num=page_num)


#### - MAXIMUM AVAILABLE PAGE ----

class MaxAvailablePageTag(StrEnum):
    TAG_TYPE = "li"
    CLASS_NAME = "pagination__page--last"

def _get_max_available_page_number_from_html(soup: BeautifulSoup) -> int:
    max_available_page = soup.find(MaxAvailablePageTag.TAG_TYPE, MaxAvailablePageTag.CLASS_NAME)
    if max_available_page is not None:
        max_page_num = max_available_page.get_text(strip=True)
    else:
        raise ValueError(f"{MaxAvailablePageTag.TAG_TYPE} tag with class '{MaxAvailablePageTag.CLASS_NAME}' not found. This is used to identify the maximum available page number.")

    try:
        return int(max_page_num)
    except:
        raise ValueError(f"Extracted '{max_page_num}', but this value could not be converted to an integer.")


#### -- STRIP INDIVIDUAL PROGRAMME EPISODE LINKS FROM LISTING PAGE ----
#### -- EXAMPLE: https://www.bbc.co.uk/programmes/b006qykl/episodes/player?page=6

def collect_listed_programme_urls_from_single_page(url: str) -> list[str]:
    html_content = get_soup_from_url(url)
    programmes_listing = html_content.find_all("div", {"class": "programme"})
    programme_urls = [
        programme.find("h2", {"class": "programme__titles"}).find("a").get("href")
        for programme in programmes_listing
    ]
    return programme_urls

#### -- MAIN FUNCTIONS FOR CRAWLING ARCHIVE ----

def get_max_archive_page_number() -> int:
    random_page_num = random.randint(10, 85)
    archive_listing = format_listing_url(page_num=random_page_num)
    html_content = get_soup_from_url(archive_listing)
    return _get_max_available_page_number_from_html(html_content)



def main():

    # get maximum number of pages available
    max_page = get_max_archive_page_number()

    if args.test:
        print(f"-> ---- [TEST MODE] ----")
    print(f"-> collecting programme urls for {max_page} available pages")


    available_page_numbers = list(range(0, (max_page + 1)))
    random.shuffle(available_page_numbers) # <- randomly shuffle order of pages

    all_programme_urls = []

    if args.test:
        available_page_numbers = available_page_numbers[:5]
    for page_num in available_page_numbers:

        listing_url = format_listing_url(page_num)
        try:
            programme_urls = collect_listed_programme_urls_from_single_page(listing_url)

            all_programme_urls.extend([
                {"listing_url": listing_url, "programme_url": programme_url}
                for programme_url in programme_urls
            ])
        except Exception as e:
            print(f"!! error collecting url {listing_url}")
            print(e)

        time.sleep(0.5)

    # write all programme urls to csv file
    all_programme_urls = pl.DataFrame(all_programme_urls, schema=["listing_url", "programme_url"])
    all_programme_urls.write_csv(PROGRAMME_URLS_CSV)
    print(f"-> Collected {len(all_programme_urls):,} individual programme urls. Saved to '{PROGRAMME_URLS_CSV}'.")
    return


if __name__ == '__main__':
    main()
