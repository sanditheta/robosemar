import numpy as np
import logging
import torch
from components.microphone import Microphone
from components.monitor import Observer, register_observers,remove_observers,notify_observers
from utilities.utils_vad import utils
from utilities.utils_numpy import convert_frames_to_numpy
from typing import Dict, List, Tuple, Callable, Union, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# SileroVAD implementation


# Strategy Registry
class VADEngineRegistry:
    _engines = {}

    @classmethod
    def register_engine(cls, engine_name: str):
        def decorator(engine_cls):
            cls._engines[engine_name] = engine_cls
            return engine_cls

        return decorator

    @classmethod
    def get_engine(cls, engine_name: str):
        return cls._engines.get(engine_name)


# VADEngine Interface


class VADEngine(ABC):
    @abstractmethod
    def infer_chunk(self, chunk: np.ndarray) -> Dict[str, Union[int, float]]:
        pass

    @abstractmethod
    def detect_voice(self, mic: Microphone) -> Tuple[Union[str, bool], int]:
        pass


@VADEngineRegistry.register_engine("silero_vad")
class SileroVAD(VADEngine):
    def __init__(self, config: Dict[str, str]) -> None:
        self.device: torch.device = torch.device(config.get("device"))
        logger.debug("load silero")
        self.model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            force_reload=False,
            onnx=True,
        )
        logger.info(f"Init VAD engine")
        (
            self.get_speech_ts,
            _save_audio,
            _read_audio,
            VADFlow,
            _collect_chunks,
        ) = utils()
        self.vad_iterator = VADFlow(
            model=self.model
        )  # Initializing VADIterator with the loaded model

    def infer_chunk(self, chunk: np.ndarray) -> Dict[str, Union[int, float]]:
        waveform: torch.Tensor = torch.from_numpy(chunk).float()
        waveform = torch.reshape(waveform, (1, len(waveform)))
        result = self.vad_iterator(
            waveform, return_seconds=True
        )  # Using VADIterator instance
        return result

    def detect_voice(self, mic: Microphone) -> Tuple[Union[str, bool], int]:
        frames, overflowed = mic.read()
        logger.debug(f"frames type: {type(frames)}")

        frames = convert_frames_to_numpy(frames)

        labels: Union[Tuple[str, int], Tuple[bool, int]] = self.infer_chunk(frames)
        status: Union[str, bool]
        timestamp: int
        status, timestamp = labels
        logger.debug(f"Speech labels: {labels}")

        if status:
            logger.debug(f"{status} at {timestamp} seconds")
            return status, timestamp
        if overflowed:
            logger.warning("Audio buffer overflowed. Some data may be lost.")
        return status, timestamp


class VoiceActivityDetection:
    """
    Class responsible for Voice Activity Detection (VAD) using a given VAD engine.
    Implements the Subject interface to notify observers of detected voice activity.
    """

    def __init__(self, vad_engine: VADEngine, microphone: Microphone) -> None:
        self.microphone = microphone
        self.vad_engine = vad_engine
        self._observers: List[Observer] = []

    def register_observers(self, observers: Union[Observer, List[Observer]]) -> None:
        register_observers(self, observers)

    def remove_observers(self, observers: Union[Observer, List[Observer]]) -> None:
        remove_observers(self, observers)

    def notify_observers(self, status: Union[str, bool], timestamp: int) -> None:
        notify_observers(self, status, timestamp)

    def one_time_vad(self, observers: List[Observer] = []) -> None:
        self.register_observers(observers)
        status = False
        while not status:
            status, timestamp = self.vad_engine.detect_voice(self.microphone)
            if status:
                self.notify_observers(status, timestamp)

    def monitor_voice(self, observers: List[Observer] = []) -> None:
        self.register_observers(observers)
        logger.info("Monitoring voice activity. Press Ctrl+C to stop.")
        while True:
            status, timestamp = self.vad_engine.detect_voice(self.microphone)
            if status:
                self.notify_observers(status, timestamp)


class VADEngineFactory:
    @staticmethod
    def build(config: Dict[str, str]) -> VADEngine:
        engine_type = config.get("engine_type")
        engine_class = VADEngineRegistry.get_engine(engine_type)
        if not engine_class:
            raise ValueError(f"Unknown VAD engine type: {engine_type}")
        return engine_class(config.get(engine_type, {}))
