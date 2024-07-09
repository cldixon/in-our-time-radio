import random
from enum import StrEnum

from bs4 import BeautifulSoup
from utils import get_html, crawl_pooler

from programme import get_programme_data_from_url

# templated path for programme episode listings
PROGRAMME_LISTING_URL_TEMPLATE = (
    "https://www.bbc.co.uk/programmes/"
    "b006qykl/"                          # <- id for 'In Our Time'
    "episodes/player?"
    "page={page_num}"                    # <- template for specifying page number
)

def format_listing_url(page_num: int, url_template: str = PROGRAMME_LISTING_URL_TEMPLATE) -> str:
    return url_template.format(page_num=page_num)


#### -- HELPER FUNCTIONS TO IDENTIFY THE MAXIMUM AVAILABLE PAGES ----

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
    html_content = get_html(url)
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
    html_content = get_html(archive_listing)
    return _get_max_available_page_number_from_html(html_content)



def collect_all_programme_urls(
    max_page: int | None = None,
    min_page: int = 1,
    url_template: str = PROGRAMME_LISTING_URL_TEMPLATE
) -> list[str]:
    if max_page is None:
        max_page = get_max_archive_page_number()
    available_page_numbers = list(range(min_page, (max_page + 1)))
    random.shuffle(available_page_numbers) # <- randomly shuffle order of pages
    programme_listing_urls = [
        format_listing_url(page_num) for page_num in available_page_numbers
    ]

    all_programme_urls = crawl_pooler(
        collect_listed_programme_urls_from_single_page,
        programme_listing_urls,
        sleep_time=1,
        processes=4
    )

    # flatten nested list of programme urls
    return [i for sublist in all_programme_urls for i in sublist]


def collect_all_programme_data(programme_urls: list[str] | None = None) -> list[dict]:
    if programme_urls is None:
        programme_urls = collect_all_programme_urls()

    all_programm_data = crawl_pooler(
        crawl_func=get_programme_data_from_url,
        target_urls=programme_urls,
        sleep_time=1,
        processes=4
    )
    return all_programm_data
