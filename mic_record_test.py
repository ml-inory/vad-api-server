from mic import Mic
import soundfile as sf

# 定义测试麦克风的函数
def test_microphone(device_index=None, output_filename="mic_record_test.wav"):
    # 设置录音参数
    duration = 5  # 录音时长（秒）
    fs = 44100  # 采样频率

    mic = Mic(device_index)

    print("Recording...")
    # 使用sounddevice录制声音
    recording = mic.record(duration)

    print("Recording finished.")

    # 保存录音为WAV文件
    sf.write(output_filename, recording, mic.sample_rate)

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
