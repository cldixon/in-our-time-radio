
import polars as pl
from faster_whisper import WhisperModel

#model_size = "large-v3"
model_size = "medium"

# Run on GPU with FP16
model = WhisperModel(model_size, device="cpu", compute_type="float32")


TEST_AUDIO_SAMPLE = "data/micro_test_sample.wav"

segments, info = model.transcribe(TEST_AUDIO_SAMPLE, beam_size=5)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

#for segment in segments:
#    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

segments_df = pl.DataFrame([
    {"start": segment.start, "end": segment.end, "text": segment.text}
    for segment in segments
])

segments_df.write_csv("data/faster_whisper_test_result.csv")

print(f"types --> segments: {type(segments)} | info: {type(info)}...")
