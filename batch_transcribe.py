import os
import time
import json
import argparse
from pathlib import Path
from typing import TypedDict
from timeit import default_timer as timer

import mlx_whisper
from tqdm import tqdm

MODEL_CHECKPOINT = "mlx-community/distil-whisper-large-v3"
SUPPORTED_AUDIO_FORMATS = [".mp3", ".wav"]


parser = argparse.ArgumentParser()

parser.add_argument(
    "--audio-dir",
    type=Path,
    required=True,
    help="Input directory containing audio files."
)

parser.add_argument(
    "-o",
    "--outdir",
    type=str,
    required=False,
    default=".",
    help="Location to save output data. Output format depends on input format (i.e., single file vs. directory of audio files)."
)

parser.add_argument(
    "--backfill",
    action="store_true",
    required=False,
    help="Flag for performing backfill of transcriptions. With this enabled, will only transcribe files from provided data directory which are not already transcribed in output directory."
)

args = parser.parse_args()


def is_valid_audio_file(filename: Path | str) -> bool:
    ## NOTE: I know there are some other formats supported.
    return os.path.splitext(os.path.basename(filename))[1] in SUPPORTED_AUDIO_FORMATS



class AudioFile(TypedDict):
    filepath: str
    id: str

def get_file_id(filepath: str) -> str:
    return os.path.splitext(os.path.basename(filepath))[0]


def create_audio_file_dict(filepath: str) -> AudioFile:
    return AudioFile(
        filepath = filepath,
        id = get_file_id(filepath)
    )


def main():
    ## ---- PROCESS INPUTS ------

    ## quality control check on input audio directory
    audio_dir = args.audio_dir
    assert os.path.exists(audio_dir) and os.path.isdir(audio_dir), f"Invalid input for audio directory."

    ## get list of audio files from input directory + quality control check
    audio_files = [os.path.join(audio_dir, file) for file in os.listdir(audio_dir)]
    audio_files = [create_audio_file_dict(audio_filepath) for audio_filepath in audio_files]
    assert len(audio_files) > 0, f"Audio directory '{audio_dir}' is empty. Must contain audio files."
    assert all([is_valid_audio_file(file["filepath"]) for file in audio_files]), f"Detected a file in directory '{audio_dir}' with a file extension other than '.mp3' or '.wav'. This script expects only audio files."

    ## check on provided output directory
    output_dir = args.outdir

    # conditionally create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # for backfill mode, check which audio files need to be transcribed
    if args.backfill:
        already_transcribed_files = os.listdir(output_dir)
        already_transcribed_ids = [get_file_id(file) for file in already_transcribed_files]

        not_yet_transcribed_files = [file for file in audio_files if file["id"] not in already_transcribed_ids]
        audio_files = not_yet_transcribed_files




    ## ---- BEGIN TRANSCRIPTION ------
    num_audio_files = len(audio_files)
    print(f"## Transcribing {num_audio_files:,} Audio File(s)\n{'-' * 35}")

    for idx, file in enumerate(audio_files):
        start_time = timer()
        transcribed = mlx_whisper.transcribe(file["filepath"], path_or_hf_repo=MODEL_CHECKPOINT)
        total_time = timer() - start_time

        # save to json file
        output_filepath = os.path.join(output_dir, f"{file['id']}.json")
        with open(output_filepath, mode="w") as outfile:
            json.dump(transcribed, outfile)
            outfile.close()

        print(f"-> file {idx+1}/{num_audio_files} | transcribed '{file['filepath']}' in {round(total_time)}s | saved to '{output_filepath}'")

    print("Done.")



    return

if __name__ == '__main__':
    main()
