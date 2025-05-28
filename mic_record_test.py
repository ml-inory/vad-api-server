from mic import Mic
import soundfile as sf
import time
import numpy as np
import pyaudio


# 定义测试麦克风的函数
def test_microphone(device_index=None, output_filename="mic_record_test.wav"):
    # 设置录音参数
    duration = 5  # 录音时长（秒）
    fs = 44100  # 采样频率

    mic = Mic(device_index, fs)

    audio = []
    def record_callback(in_data, frame_count, time_info, status):
        # 将音频数据转换为NumPy数组
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        
        # 在此处添加音频处理逻辑
        audio.append(audio_data)
        
        return (in_data, pyaudio.paContinue)

    print("Recording...")
    mic.open(record_callback)

    start = time.time()
    #  当音频流处于活动状态且录音时间未达到设定时长时
    while mic.is_active() and (time.time() - start) < duration:
        time.sleep(0.1)

    print("Recording finished.")
    mic.close()

    # 保存录音为WAV文件
    sf.write(output_filename, np.concatenate(audio, axis=-1), mic.sample_rate)

    print(f"File saved as {output_filename}")

# 主函数入口
if __name__ == "__main__":
    # 获取麦克风列表并打印
    devices = Mic.query_devices()[:5]
    for i, device in enumerate(devices):
        print(f"{i}: {device['name']}")

    # 用户输入选择麦克风设备索引
    device_index = int(input("Enter the index of the microphone to use: "))
    test_microphone(device_index)
