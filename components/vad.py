import numpy as np
import logging
import torch
from components.microphone import Microphone
from utilities.utils_vad import utils
from typing import Dict, List, Tuple, Callable, Union

logger = logging.getLogger(__name__)

# Strategy Registry
VAD_ENGINE_REGISTRY = {}


# Register Decorator
def register_vad_engine(engine: str):
    def decorator(cls):
        VAD_ENGINE_REGISTRY[engine] = cls
        return cls

    return decorator


@register_vad_engine("silero_vad")
class SileroVAD:
    def __init__(self, config: Dict[str, str]) -> None:
        self.device: torch.device = torch.device(config["device"])
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

    def detect_voice(self, chunk: np.ndarray) -> Dict[str, Union[int, float]]:
        waveform: torch.Tensor = torch.from_numpy(chunk).float()
        waveform = torch.reshape(waveform, (1, len(waveform)))
        result = self.vad_iterator(
            waveform, return_seconds=True
        )  # Using VADIterator instance
        return result


class VoiceActivityDetection:
    """
    Class responsible for Voice Activity Detection (VAD) using the snakers4/silero-vad library.
    """

    def __init__(self, config: Dict[str, str], microphone: Microphone) -> None:
        self.microphone = microphone
        self.sampling_rate: int = int(config["samplerate"])
        self.buffer: List[np.ndarray] = []
        self.engine_type: str = str(config["engine_type"])
        self.total_samples_processed = 0
        vad_engine_cls = VAD_ENGINE_REGISTRY.get(self.engine_type)
        self.vad_engine = vad_engine_cls(config[self.engine_type])

    def _convert_frames_to_numpy(self, frames: Union[bytes, np.ndarray]) -> np.ndarray:
        if self.microphone.stream_type == "raw":
            return np.frombuffer(frames, dtype=np.float32)
        elif self.microphone.stream_type == "numpy":
            return frames
        else:
            raise ValueError(f"Unsupported stream type: {self.microphone.stream_type}")

    def one_time_vad(self) -> None:
        status = False

        while not status:
            frames, overflowed = self.microphone.read()
            logger.debug(f"frames type: {type(frames)}")

            if self.microphone.stream_type == "raw":
                frames: np.ndarray = self._convert_frames_to_numpy(frames)

            labels: Union[
                Tuple[str, int], Tuple[bool, int]
            ] = self.vad_engine.detect_voice(frames)
            status: Union[str, bool]
            timestamp: int
            status, timestamp = labels
            logger.debug(f"Speech labels: {labels}")

            if status:
                logger.info(f"{status} at {timestamp} seconds")
                # callback(timestamps)
            if overflowed:
                logger.warning("Audio buffer overflowed. Some data may be lost.")

    def monitor_voice(self, callback: Callable[[List[Tuple[int, int]]], None] = None) -> None:
        logger.info("Monitoring voice activity. Press Ctrl+C to stop.")
        while True:
            frames, overflowed = self.microphone.read()
            logger.debug(f"frames type: {type(frames)}")

            if self.microphone.stream_type == "raw":
                frames: np.ndarray = self._convert_frames_to_numpy(frames)

            labels: Union[
                Tuple[str, int], Tuple[bool, int]
            ] = self.vad_engine.detect_voice(frames)
            status: Union[str, bool]
            timestamp: int
            status, timestamp = labels
            logger.debug(f"Speech labels: {labels}")

            if status:
                logger.info(f"{status} at {timestamp} seconds")
                # callback(timestamps)
            if overflowed:
                logger.warning("Audio buffer overflowed. Some data may be lost.")
