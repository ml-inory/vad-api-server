import sounddevice as sd


class Mic:
    def __init__(self, device_index=0, sample_rate=16000):
        self.device_index = device_index
        self.devices = self.query_devices()
        self.sample_rate = sample_rate

    @staticmethod
    def query_devices():
        devices = sd.query_devices()
        return devices
    
    def set_device(self, device_index: int):
        assert device_index < len(self.devices), f"device_index {device_index} exceed device num {len(self.devices)}"
        self.device_index = device_index

    def get_device(self) -> int:
        return self.device_index
    
    def get_device_name(self) -> str:
        return self.devices[self.device_index]
    
    def record(self, duration :float = 1.0):
        audio = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype="float32")
        sd.wait()
        return audio.flatten()
