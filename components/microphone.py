import sounddevice as sd
from typing import Dict, Tuple, Union
import logging
import numpy as np

logger = logging.getLogger(__name__)

STREAM_REGISTRY = {}


def register_stream(engine: str):
    def decorator(cls):
        STREAM_REGISTRY[engine] = cls
        return cls

    return decorator

@register_stream("sounddevice")
class SounddeviceStream:
    def __init__(self, config: Dict[str, str]):
        self.channels: int = int(config["channels"])
        self.samplerate: int = int(config["samplerate"])
        self.device_index: int = int(config["device_index"])
        self.chunk: int = int(config["chunk"])
        self.dtype: str = str(config["dtype"])
        self.stream_type = config["sounddevice"]["stream_type"]
        self.stream_cls = None
        input_stream_registry = {"raw": sd.RawInputStream,
                       "numpy": sd.InputStream}

        self.stream_cls = input_stream_registry.get(self.stream_type, None)

        if self.stream_cls == None:
            raise ValueError(f"Unknown stream type: {self.stream_type}")
        
        self.stream = self.stream_cls(
            channels=self.channels,
            samplerate=self.samplerate,
            device=self.device_index,
            blocksize=self.chunk,
            dtype=self.dtype,
         )
        
    def start(self):
        self.stream.start()

    def stop(self):
        self.stream.stop()
        self.stream.close()

    def read(self):
        return self.stream.read(self.chunk)

class Microphone:

    def __init__(self, config: Dict[str, str]) -> None:

        self.channels: int = int(config["channels"])
        self.samplerate: int = int(config["samplerate"])
        self.device_index: int = int(config["device_index"])
        self.chunk: int = int(config["chunk"])
        self.dtype: str = str(config["dtype"])
        self.engine_type: str = config["engine_type"]
        self.stream_type = str(config[self.engine_type]["stream_type"])
        self.stream_cls = STREAM_REGISTRY.get(self.engine_type, None)

        if self.stream_cls is None:
            raise ValueError(f"Unknown engine type: {self.engine_type}")

        self.streamer = self.stream_cls(config)
        self.streamer.start()
        logger.info("Microphone initialized.")

    def read(self) -> Union[Tuple[bytes, bool], Tuple[np.ndarray, bool]]:

        frames, overflowed = self.streamer.read()
        logger.debug(f"Frames read from the microphone: {frames}")
        return frames, overflowed

    def stop(self) -> None:

        if self.streamer is not None:
            self.streamer.stop()
            #self.streamer.close()
            self.streamer = None
            logger.info("Microphone recording stopped.")
