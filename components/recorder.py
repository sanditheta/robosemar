import soundfile as sf
import os
import numpy as np
from components.microphone import Microphone
from typing import Dict
import logging
from abc import ABC, abstractmethod

RECORDING_STRATEGY_REGISTRY = {}


def register_recording_strategy(engine: str):
    def decorator(cls):
        RECORDING_STRATEGY_REGISTRY[engine] = cls
        return cls

    return decorator


@register_recording_strategy('raw')
class RawRecordingStrategy:
    def record(self, microphone: Microphone, duration: int) -> np.ndarray:
        recorded_data = bytearray()
        for _ in range(int(microphone.samplerate * duration / microphone.chunk)):
            frames, _ = microphone.read()
            recorded_data.extend(frames)
        return np.frombuffer(recorded_data, dtype=np.float32).reshape(-1, microphone.channels)

@register_recording_strategy('numpy')
class NumpyRecordingStrategy:
    def record(self, microphone: Microphone, duration: int) -> np.ndarray:
        frames_list = []
        for _ in range(int(microphone.samplerate * duration / microphone.chunk)):
            frames, _ = microphone.read()
            frames_list.append(frames)
        recorded_data = np.concatenate(frames_list).reshape(-1, microphone.channels)
        return recorded_data

class Recorder:
    def __init__(self, config: Dict[str, str], microphone: Microphone) -> None:
        self.microphone = microphone
        self.directory: str = config['directory']
        self.filename: str = config['filename']
        self.duration: int = int(config['duration'])
        
        # Use the registry to fetch the appropriate stream factory
        strategy_class = RECORDING_STRATEGY_REGISTRY.get(self.microphone.stream_type, None)
        if strategy_class is None:
            raise ValueError(f"Unknown strategy name: {self.microphone.stream_type}")
        self.strategy = strategy_class()

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        logging.info("Recorder initialized.")

    def record_voice(self) -> None:
        logging.info("Recording started...")
        file_path = os.path.join(self.directory, self.filename)
        recorded_data = self.strategy.record(self.microphone, self.duration)
        sf.write(file_path, recorded_data, self.microphone.samplerate)
        logging.info(f"Recording saved to {file_path}")