# instantiate the pipeline
from pyannote.audio import Pipeline

from pyannote.audio.pipelines.utils.hook import ProgressHook


pipeline = Pipeline.from_pretrained(
  "pyannote/speaker-diarization-3.1",
  use_auth_token="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"
)

# run the pipeline on an audio file
with ProgressHook() as hook:
    diarization = pipeline(
        "data/test_sample.wav",
        hook=hook
    )

# dump the diarization output to disk using RTTM format
with open("audio.rttm", "w") as rttm:
    diarization.write_rttm(rttm)
