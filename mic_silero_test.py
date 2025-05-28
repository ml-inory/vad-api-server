MODEL_PATH = "./silero_vad.onnx"
from SileroOrt import SileroOrt
from utils_vad import *
from mic import Mic
import os
from datetime import datetime
import soundfile as sf

os.makedirs("mic_silero_test", exist_ok=True)

mic = Mic(1, 16000)

model = SileroOrt(MODEL_PATH)
prob_thresh = 0.5
window_size_samples = 512
record_duration = 1
speech_continue_ms = 500

cur_start = None
prev_end = None
audio_chunks = []
while True:
    if len(audio_chunks) == 0:
        start_time = datetime.now().strftime("%Y%m%d%H%M%S")

    audio = mic.record(record_duration)
    speech_timestamps = get_speech_timestamps(audio, model, sampling_rate=mic.sample_rate)

    if len(speech_timestamps) > 0:
        cur_start = speech_timestamps[0]["start"]
        if prev_end is not None:
            prev_left_ms = (record_duration * mic.sample_rate - prev_end) * 1000 / mic.sample_rate
            cur_left_ms = cur_start * 1000 / mic.sample_rate
            blank_ms = prev_left_ms + cur_left_ms

            if blank_ms > speech_continue_ms:
                end_time = datetime.now().strftime("%Y%m%d%H%M%S")
                sf.write(f"mic_silero_test/{start_time}-{end_time}.wav", np.concatenate(audio_chunks, axis=-1), mic.sample_rate)

                audio_chunks = []
        prev_end = speech_timestamps[-1]["end"]
    else:
        if len(audio_chunks):
            end_time = datetime.now().strftime("%Y%m%d%H%M%S")
            sf.write(f"mic_silero_test/{start_time}-{end_time}.wav", np.concatenate(audio_chunks, axis=-1), mic.sample_rate)

            audio_chunks = []
            cur_start = None
            prev_end = None
    