import os
import time
import argparse
from pathlib import Path

import requests
import polars as pl
from tqdm import tqdm

from utils import DEFAULT_HEADERS

parser = argparse.ArgumentParser()

parser.add_argument("--test", action="store_true", help="Flag for testing on small number of html file.")

args = parser.parse_args()


## set data directory
DATA_DIR = "data"
PROGRAMME_MP3_DIR = os.path.join(DATA_DIR, "audio_files")


def download_mp3_from_url(url: str, dirpath:Path | str) -> None:
    mp3_content = requests.get(url, headers=DEFAULT_HEADERS)

    # create filename
    filepath = os.path.join(dirpath, os.path.basename(url))

    with open(filepath, mode="wb") as outfile:
        outfile.write(mp3_content.content)
        outfile.close()
    return


def main():

    ## load parsed programme data
    programme_data = pl.read_parquet("data/programme_data.parquet")

    audio_file_urls = (
        programme_data
        .select(pl.col("audio_url"))
        .to_series().to_list()
    )
    audio_file_urls = [audio_url for audio_url in audio_file_urls if audio_url is not None]
    print(f"-> Downloading {len(audio_file_urls):,} mp3 files.")

    if args.test:
        print(f"-> [TEST MODE] ----")

    if args.test:
        audio_file_urls = audio_file_urls[:5]

    error_counter = 0
    for audio_url in tqdm(audio_file_urls):
        try:
            download_mp3_from_url(audio_url, dirpath=PROGRAMME_MP3_DIR)
            time.sleep(0.5)

        except Exception as e:
            print(f"!! error downloading mp3 from url '{audio_url}'.")
            print(e)
            error_counter += 1

    print(f"-> {error_counter} errors.")


    return

if __name__ == "__main__":
    main()
