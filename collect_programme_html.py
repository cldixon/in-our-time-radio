import os
import time
import argparse

import polars as pl

from utils import get_html_from_url, save_html_to_file

parser = argparse.ArgumentParser()

parser.add_argument("--file", type=str, required=False, help="Path to csv file containing starting programme urls.")
parser.add_argument("--url", type=str, required=False, help="URL for specific programme webpage.")
parser.add_argument("--test", action="store_true", help="Flag for testing on small number of urls.")
args = parser.parse_args()

## set data directory
DATA_DIR = "data"
PROGRAMME_HTML_DIR = os.path.join(DATA_DIR, "programme_html")

if not os.path.exists(PROGRAMME_HTML_DIR):
    os.mkdir(PROGRAMME_HTML_DIR)



def main():

    ## load csv file containing all programme urls
    ## see `listings.py`
    programme_urls = (
        pl.read_csv(args.file)
        .select("programme_url")
        .to_series().to_list()
    )

    if args.test:
        print(f"-> ---- [TEST MODE] ----")

    print(f"-> Saving {len(programme_urls):,} episode webpages to '{HTML_OUTPUT_DIR}'.")


    if args.test:
        programme_urls = programme_urls[:5]

    save_counter = 0
    num_errors = 0

    for url in programme_urls:
        try:
            html = get_html_from_url(url)

            # create programme filename
            output_filepath = os.path.join(
                PROGRAMME_HTML_DIR,
                f"{os.path.basename(url)}.html"
            )
            save_html_to_file(html, filepath=output_filepath)
            save_counter += 1
            time.sleep(0.5)

        except Exception as e:
            print(f"!! error downloading html for url '{url}'.")
            print(e)
            num_errors += 1

    print(f"-> Saved {save_counter:,} programme pages to file.\n-> {num_errors:,} errors.")

    return


if __name__ == "__main__":
    main()
