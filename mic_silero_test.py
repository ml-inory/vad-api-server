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

# 获取麦克风列表并打印
devices = Mic.query_devices()[:5]
for i, device in enumerate(devices):
    print(f"{i}: {device['name']}")

# 用户输入选择麦克风设备索引
device_index = int(input("Enter the index of the microphone to use: "))

mic = Mic(1, 16000)

model = SileroOrt(MODEL_PATH)
prob_thresh = 0.2
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
    while audio_chunks_len < window_size_samples:
        continue

    if len(audio_chunks) > 1:
        audio = np.concatenate(audio_chunks, axis=-1)
    else:
        audio = audio_chunks[0]
    audio_chunks = []
    audio_chunks_len = 0

    if len(audio_with_speech) == 0:
        start_time = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # speech_timestamps = get_speech_timestamps(audio, model, threshold=prob_thresh, sampling_rate=mic.sample_rate)
    # print(speech_timestamps)
    speech_probs = []
    real_width = len(audio)
    padded_width = int(np.ceil(len(audio) / window_size_samples) * window_size_samples)
    audio = np.pad(audio, (0, padded_width - len(audio)))
    for i in range(0, len(audio), window_size_samples):
        chunk = audio[i: i+window_size_samples]
        speech_prob = model(chunk).item()
        speech_probs.append(speech_prob)
    model.reset_states() # reset model states after each audio

    for i, prob in enumerate(speech_probs):
        chunk = audio[i * window_size_samples : (i + 1) * window_size_samples]
        if i == len(speech_probs) - 1:
            chunk = chunk[:window_size_samples - (padded_width - real_width)]
        if prob > prob_thresh:
            audio_with_speech.append(chunk)
            silence_ms = 0
        else:
            if len(audio_with_speech) > 0:
                # silence
                silence_ms += len(chunk) / mic.sample_rate * 1000

                if silence_ms > speech_continue_ms:
                    end_time = datetime.now().strftime("%Y%m%d%H%M%S")
                    print(f"start: {start_time}  end: {end_time}")
                    sf.write(f"mic_silero_test/{start_time}-{end_time}.wav", np.concatenate(audio_with_speech, axis=-1), mic.sample_rate)

                    audio_with_speech = []
                    silence_ms = 0
                else:
                    audio_with_speech.append(chunk)