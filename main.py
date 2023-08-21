import logging
from utilities.config import ConfigurationManager as Config
from components.cli import CLI
from components.microphone import Microphone
from components.recorder import Recorder
from components.vad import VoiceActivityDetection
from typing import List, Tuple


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define a callback function to handle detected speech
def detected_speech_callback(timestamps: List[Tuple[int, int]]) -> None:
    for start, end in timestamps:
        print(
            f"Detected speech from {timestamps[0]['start']} to {timestamps[0]['end']}"
        )


def main():
    # Load configuration
    config = Config("config/config.yaml")

    # Initialize components
    microphone_config = config.get("microphone")
    microphone = Microphone(config=microphone_config)

    # Parse CLI arguments
    args = CLI.parse_args()

    # Process command
    if args.test_mic:
        recorder_config = config.get("recorder")
        recorder = Recorder(config=recorder_config, microphone=microphone)
        recorder.record_voice()
    elif args.detect_speech:
        vad_config = config.get("vad")
        vad = VoiceActivityDetection(
            config=vad_config, microphone=microphone
        )
        # Monitor voice activity
        vad.monitor_voice()
    else:
        CLI.show_usage()


if __name__ == "__main__":
    main()
