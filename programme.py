import re
from bs4 import BeautifulSoup


## -- PROGRAMME PAGE PARSING ----

def get_title(programme_html: BeautifulSoup) -> str:
    return (
        programme_html
        .find("div", {"class": "island"})
        .find("h1", {"class": "no-margin"})
        .get_text(strip=True)
    )

def get_duration(programme_html: BeautifulSoup) -> int:
    duration_as_seq = (
        programme_html
        .find("div", {"class": "map__intro"})
        .get_text(strip=True, separator=" ")
    )
    if duration_as_seq is not None:
        duration_as_str = re.search(r"(\d{1,3}) minutes$", duration_as_seq).group(1)
        return int(duration_as_str)
    else:
        raise ValueError(f"Unable to extract duration...")


def get_short_description(programme_html: BeautifulSoup) -> str:
    return programme_html.find("div", {"class": "synopsis-toggle__short"}).find("p").get_text(strip=True)

def get_long_description(programme_html: BeautifulSoup) -> str:
    return (
        programme_html.find("div", {"class": "synopsis-toggle__long"})
        .get_text(strip=True, separator="\n")
    )


def get_download_url(programme_html: BeautifulSoup) -> str:
    download_path = programme_html.find("div", {"class": "buttons__download"}).find("a").get("href")
    return f"https:{download_path}"

def get_cover_photo_url(programme_html: BeautifulSoup) -> str:
    return programme_html.find("img", {"class": "image"}).get("src")

def extract_programme_data_from_html(programme_html: BeautifulSoup) -> dict:
    # FIXME: create typed dictionary over std dict
    return {
        "title": get_title(programme_html),
        "duration": get_duration(programme_html),
        "short_description": get_short_description(programme_html),
        "long_description": get_long_description(programme_html),
        "download_url": get_download_url(programme_html),
        "photo_url": get_cover_photo_url(programme_html)
    }
