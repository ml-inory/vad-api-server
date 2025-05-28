MODEL_PATH = "./silero_vad.onnx"
from SileroOrt import SileroOrt
from utils_vad import *
from mic import Mic
import os
from datetime import datetime
import soundfile as sf
import pyaudio
import time

os.makedirs("mic_silero_test", exist_ok=True)

mic = Mic(1, 16000)

model = SileroOrt(MODEL_PATH)
prob_thresh = 0.5
window_size_samples = 512
record_duration = 0.5
speech_continue_ms = 1000

audio_chunks = []
audio_chunks_len = 0
silence_ms = 0
audio_with_speech = []

def record_callback(in_data, frame_count, time_info, status):
    global audio_chunks, audio_chunks_len
    # 将音频数据转换为NumPy数组
    audio_chunks.append(np.frombuffer(in_data, dtype=np.float32))
    audio_chunks_len += frame_count
    
    return (in_data, pyaudio.paContinue)

mic.open(record_callback)

while True:
    while audio_chunks_len < record_duration * mic.sample_rate:
        time.sleep(0.1)
        continue

    audio = np.concatenate(audio_chunks, axis=-1)
    audio_chunks = []
    audio_chunks_len = 0

    if len(audio_with_speech) == 0:
        start_time = datetime.now().strftime("%Y%m%d%H%M%S")
    
    speech_timestamps = get_speech_timestamps(audio, model, sampling_rate=mic.sample_rate)
    print(speech_timestamps)
    if len(speech_timestamps) > 0:
        print(f'start: {speech_timestamps[0]["start"]}  end: {speech_timestamps[-1]["end"]}')
        audio_with_speech.append(audio)
        silence_ms = 0
    else:
        # silence
        if len(audio_with_speech):
            silence_ms += record_duration * 1000

            if silence_ms > speech_continue_ms:
                end_time = datetime.now().strftime("%Y%m%d%H%M%S")
                sf.write(f"mic_silero_test/{start_time}-{end_time}.wav", np.concatenate(audio_with_speech, axis=-1), mic.sample_rate)

                audio_with_speech = []
                silence_ms = 0