import pyaudio
from typing import Callable


class Mic:
    def __init__(self, device_index=0, sample_rate=16000):
        self.device = pyaudio.PyAudio()
        self.device_index = device_index
        self.sample_rate = sample_rate
        self.stream = None

    @staticmethod
    def query_devices():
        device = pyaudio.PyAudio()
        device_num = device.get_device_count()
        device_names = [device.get_device_info_by_index(i) for i in range(device_num)]
        device.terminate()
        return device_names
    
    def set_device(self, device_index: int):
        assert device_index < len(self.devices), f"device_index {device_index} exceed device num {len(self.devices)}"
        self.device_index = device_index

    def get_device(self) -> int:
        return self.device_index
    
    def open(self, callback: Callable):
        self.close()
        self.stream = self.device.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=self.sample_rate,
                    input=True,
                    output=False,
                    input_device_index=self.device_index,
                    stream_callback=callback)

    def close(self):
        if self.stream is not None:
            self.stream.close()

    def is_active(self) -> bool:
        if self.stream is None:
            return False
        else:
            return self.stream.is_active()


