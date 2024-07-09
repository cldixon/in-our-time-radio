import os
import re
import random
from datetime import datetime

import requests
import polars as pl
from bs4 import BeautifulSoup

import archive
from utils import get_html
from programme import get_programme_data_from_url

# set output values
DATA_DIR = "data"




def main():
    print(f"# -- Programme Archive Bulk Collection ----")

    ## -- STAGE 1: COLLECT ALL PROGRAMME URLS FROM ARCHIVE----
    print(f"\n## -- COLLECTING PROGRAMME URLS FROM LISTINGS ----\n{'-' * 35}")
    programme_urls = archive.collect_all_programme_urls()
    print('-' * 35, '\n')

    ## -- STAGE 2.0: SCRAPE PROGRAMME CONTENT ----
    print(f"\n## -- COLLECTING PROGRAMME DATA ----\n{'-' * 35}")
    programme_data = archive.collect_all_programme_data(programme_urls)
    print('-' * 35, '\n')


    #### -- convert programme data to table
    programme_data = pl.DataFrame(programme_data)
    print(programme_data)
    programme_data.write_parquet(os.path.join(DATA_DIR, "programme_data.parquet"))

    return


if __name__ == '__main__':
    main()
