import re
from typing import TypedDict

from bs4 import BeautifulSoup

from utils import get_html


## -- PROGRAMME PAGE PARSING ----

def get_title(programme_html: BeautifulSoup) -> str:
    return (
        programme_html
        .find("div", {"class": "island"})
        .find("h1", {"class": "no-margin"})
        .get_text(strip=True)
    )

def get_duration(programme_html: BeautifulSoup) -> int:
    """Show duration. Can be desribed in minutes (e.g., '43 minutes') or in hours (e.g., '1 hour')."""
    duration = (
        programme_html
        .find("div", {"class": "map__intro"})
    )
    if duration is not None:
        return duration.find_all("p")[1].get_text(strip=True)
    else:
        raise ValueError(f"Unable to extract duration...")


def get_short_description(programme_html: BeautifulSoup) -> str:
    return programme_html.find("div", {"class": "synopsis-toggle__short"}).find("p").get_text(strip=True)

def get_long_description(programme_html: BeautifulSoup) -> str:
    return (
        programme_html.find("div", {"class": "synopsis-toggle__long"})
        .get_text(strip=True, separator="\n")
    )


# NOTE: newer episodes do not offer a download button...
def get_download_url(programme_html: BeautifulSoup) -> str | None:
    download_button_tag = programme_html.find("div", {"class": "buttons__download"})
    if download_button_tag:
        download_path = download_button_tag.find("a").get("href")
        return f"https:{download_path}"
    return None

def get_cover_photo_url(programme_html: BeautifulSoup) -> str:
    return programme_html.find("img", {"class": "image"}).get("src")

class BroadcastTime(TypedDict):
    date: str
    time: str

def get_previous_broadcasts(programme_html: BeautifulSoup) -> list[dict]:
    prev_broadcast_tags = (
        programme_html
        .find("div", {"id": "broadcasts"})
        .find_all("div", {"class": "broadcast-event__time"})
    )
    if prev_broadcast_tags:
        extracted_prev_broadcast_data = []
        for tag in prev_broadcast_tags:
            # get text spans
            text_spans = tag.find_all("span")
            extracted_prev_broadcast_data.append(
                BroadcastTime(
                    date=text_spans[0].get_text(strip=True),
                    time=text_spans[1].get_text(strip=True)
                )
            )
        return extracted_prev_broadcast_data



def get_credits(programme_html: BeautifulSoup) -> list[dict] | None:
    credits_tag = programme_html.find("div", {"id": "credits"})
    if credits_tag:
        extracted_credits = []
        credits_table_rows = credits_tag.find("table").find("tbody").find_all("tr")
        for table_row in credits_table_rows:
            row_data = table_row.find_all("td")
            extracted_credits.append({
                "role": row_data[0].get_text(strip=True),
                "name": row_data[1].get_text(strip=True)
            })
        return extracted_credits
    return

class FeaturedCollection(TypedDict):
    title: str
    description: str

def get_featured_collections(programme_html: BeautifulSoup) -> list[FeaturedCollection] | None:
    feature_section_tag = programme_html.find("div", {"id": "collections"})
    if feature_section_tag:
        collections_list = feature_section_tag.find("ul").find_all("li")
        feature_collections = []
        for collection in collections_list:
            feature_collections.append(
                FeaturedCollection(
                    title=collection.find("span", {"class": "programme__title"}).get_text(strip=True),
                    description=collection.find("p", {"class": "programme__synopsis"}).get_text(strip=True)
                )
            )
        return feature_collections
    return None

def get_related_links(programme_html: BeautifulSoup) -> list[dict] | None:
    related_links_section = programme_html.find("div", {"id": "related_links"})
    if related_links_section:
        links_list = related_links_section.find("ul").find_all("li")
        related_links = []
        for list_item in links_list:
            related_links.append({
                "title": list_item.find("a").get_text(strip=True),
                "url": list_item.find("a").get("href")
            })
        return related_links
    return


def extract_programme_data_from_html(programme_html: BeautifulSoup) -> dict:
    # FIXME: create typed dictionary over std dict
    return {
        "title": get_title(programme_html),
        "duration": get_duration(programme_html),
        "short_description": get_short_description(programme_html),
        "long_description": get_long_description(programme_html),
        "audio_url": get_download_url(programme_html),
        "photo_url": get_cover_photo_url(programme_html),
        "previous_broadcasts": get_previous_broadcasts(programme_html),
        "credits": get_credits(programme_html), # <- older episodes do not have this section
        "featured_collections": get_featured_collections(programme_html),
        "related_links": get_related_links(programme_html)
    }

def get_programme_data_from_url(url: str) -> dict:
    programme_html = get_html(url)
    return {
        "url": url,
        "html": str(programme_html),
        **extract_programme_data_from_html(programme_html)
    }
