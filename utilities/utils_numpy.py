from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple, Callable, Union, Optional, Any
import array as _array
import mmap
from numpy._typing import NDArray

buffer_types = (bytes, bytearray, memoryview, mmap.mmap, np.ndarray, np.generic)


def convert_frames_to_numpy(frames: Union[bytes, np.ndarray]) -> np.ndarray:
    if not frames:
        raise ValueError("Provided frames are empty or None")

    try:
        frames = np.frombuffer(frames, dtype=np.float32)
    except ValueError as exc:
        raise ValueError(f"Error converting frames to numpy array: {exc}")

    return frames
