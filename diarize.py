# instantiate the pipeline
import os
import dotenv
from pyannote.audio import Pipeline

from pyannote.audio.pipelines.utils.hook import ProgressHook

dotenv.load_dotenv()
HF_AUTH_TOKEN = os.environ["HF_TOKEN"]

pipeline = Pipeline.from_pretrained(
  "pyannote/speaker-diarization-3.1",
  use_auth_token=HF_AUTH_TOKEN
)

# run the pipeline on an audio file
with ProgressHook() as hook:
    diarization = pipeline(
        "data/test_sample.wav",
        hook=hook
    )

# dump the diarization output to disk using RTTM format
with open("data/test_sample.rttm", "w") as rttm:
    diarization.write_rttm(rttm)
