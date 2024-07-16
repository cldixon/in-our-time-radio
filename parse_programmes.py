import os
import argparse

import polars as pl

from utils import get_html_from_url, get_soup_from_file
from programme import parse_programme_html_soup

parser = argparse.ArgumentParser()

parser.add_argument("--test", action="store_true", help="Flag for testing on small number of html file.")

args = parser.parse_args()

## set data directory
DATA_DIR = "data"
PROGRAMME_HTML_DIR = os.path.join(DATA_DIR, "programme_html")

def main():

    if args.test:
        print(f"-> [TEST MODE] ----")

    # get downloaded html files
    programme_html_files = os.listdir(PROGRAMME_HTML_DIR)
    print(f"-> Parsing {len(programme_html_files):,} programme html files.")

    if args.test:
        programme_html_files = programme_html_files[:5]

    error_counter = 0
    all_parsed_programme_data = []
    for file in programme_html_files:
        soup = get_soup_from_file(os.path.join(PROGRAMME_HTML_DIR, file))

        try:
            programme_data = parse_programme_html_soup(soup)
            all_parsed_programme_data.append(programme_data)
        except Exception as e:
            print(f"!! error occurred when parsing file '{file}'.")
            print(e)
            error_counter += 1

    # convert parsed data to dataframe; save as parquet
    programme_df = pl.DataFrame(all_parsed_programme_data)
    print(f"-> Parsed data for {len(programme_df):,} programme episodes.")
    print(f"-> {error_counter} errors.")

    programme_df.write_parquet(os.path.join(DATA_DIR, "programme_data.parquet"))

    return

if __name__ == "__main__":
    main()
