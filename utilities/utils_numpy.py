def convert_frames_to_numpy(self, frames: Union[bytes, np.ndarray]) -> np.ndarray:
    if isinstance(frames, bytes):
        return np.frombuffer(frames, dtype=np.float32)
    elif isinstance(frames, np.ndarray):
        return frames
    else:
        raise ValueError(f"Unsupported frame type: {type(frames)}")