import modal

app = modal.App("nvidia-smi-example")

'''
@app.function()
def square(x):
    print("This code is running on a remote worker!")
    return x**2
'''
'''
@app.function(gpu="any")
def check_nvidia_smi():
    import subprocess
    output = subprocess.check_output(["nvidia-smi"], text=True)
    assert "Driver Version: 550.54.15" in output
    assert "CUDA Version: 12.4" in output
    return output
 '''

'''
image = modal.Image.debian_slim().pip_install("torch")


@app.function(gpu="any", image=image)
def run_torch():
    import torch
    has_cuda = torch.cuda.is_available()
    print(f"It is {has_cuda} that torch can access CUDA")
    return has_cuda
'''

'''
image = modal.Image.debian_slim().pip_install("transformers[torch]")
image = image.apt_install("ffmpeg")  # for audio processing


@app.function(gpu="any", image=image)
def run_transformers():
    from transformers import pipeline
    transcriber = pipeline(model="openai/whisper-tiny.en", device="cuda")
    result = transcriber("https://modal-public-assets.s3.amazonaws.com/mlk.flac")
    print(result["text"])  # I have a dream that one day this nation will rise up live out the true meaning of its creed
'''

## -- pyannoate diarize with model -- ##
import os
from timeit import default_timer as timer

import torch
import dotenv
from pyannote.audio import Pipeline

from pyannote.audio.pipelines.utils.hook import ProgressHook

dotenv.load_dotenv()

image = modal.Image.debian_slim().pip_install([
    "transformers[torch]",
    "torchvision",
    "python-dotenv",
    "pyannote.audio"
])
image = image.apt_install("ffmpeg")  # for audio processing

@app.function(gpu="any", image=image, timeout=10_000)
def run_diarizer(filepath: str, hf_auth_token: str):
    print(f"cuda available: {torch.cuda.is_available()}")
    print(f"num devices: {torch.cuda.device_count()}")

    pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=hf_auth_token
    )
    pipeline = pipeline.to(torch.device('cuda'))

    print(f"| -> created diarization pipeline object")

    # run the pipeline on an audio file
    with ProgressHook() as hook:
        diarization = pipeline(
            filepath,
            hook=hook
        )
    print(f"| -> performed pipeline inference for audion file")
    return diarization



@app.local_entrypoint()
def main():
    HF_AUTH_TOKEN = os.environ["HF_TOKEN"]
    filepath = "modal_test/p02q5kk7.wav"
    start_timer = timer()
    diarization = run_diarizer.remote(filepath, HF_AUTH_TOKEN)
    print(f"!! completed diarization in {(timer() - start_timer):.0f} secs")


    # dump the diarization output to disk using RTTM format
    base_filename = os.path.basename(os.path.splitext(filepath)[0])
    rttm_fileout = f"modal_test/{base_filename}.rttm"
    with open(rttm_fileout, "w") as rttm:
        diarization.write_rttm(rttm)
    print(f"| -> saved output to rttm file")
