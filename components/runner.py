from abc import ABC, abstractmethod
from components.cli import CLI
from components.monitor import VoiceLogger
from components.microphone import Microphone
from components.recorder import Recorder
from components.vad import VoiceActivityDetection, VADEngineFactory
from utilities.config import ConfigurationManager


class ActionStrategy(ABC):
    @abstractmethod
    def execute(self):
        pass


class TestMicStrategy(ActionStrategy):
    def __init__(self, recorder):
        self.recorder = recorder

    def execute(self):
        self.recorder.record_voice()


class DetectSpeechStrategy(ActionStrategy):
    def __init__(self, vad):
        self.vad = vad

    def execute(self):
        voice_logger = VoiceLogger()
        self.vad.register_observers([voice_logger])
        self.vad.monitor_voice()


class ShowUsageStrategy(ActionStrategy):
    def execute(self):
        CLI.show_usage()


class StrategyRunner:
    def __init__(self, strategy: ActionStrategy):
        self.strategy = strategy

    def run(self):
        self.strategy.execute()


def initialize_components(config_manager: ConfigurationManager):
    """
    Initialize the main components: Microphone, Recorder, and VAD.

    Args:
    - config_manager (ConfigurationManager): The configuration manager instance.

    Returns:
    - tuple: Initialized instances of Microphone, Recorder, and VAD.
    """

    microphone_config = config_manager.get("microphone", {})
    recorder_config = config_manager.get("recorder", {})
    vad_config = config_manager.get("vad", {})

    microphone = Microphone(microphone_config)
    recorder = Recorder(recorder_config, microphone)
    vad_engine = VADEngineFactory.build(vad_config)
    vad = VoiceActivityDetection(vad_engine, microphone)

    return microphone, recorder, vad


def select_strategy(args, recorder, vad):
    """
    Select the appropriate strategy based on the CLI arguments.

    Args:
    - args: Parsed CLI arguments.
    - recorder: Recorder instance.
    - vad: VAD instance.

    Returns:
    - ActionStrategy: The chosen strategy instance.
    """
    if args.test_mic:
        return TestMicStrategy(recorder)
    elif args.detect_speech:
        return DetectSpeechStrategy(vad)
    else:
        return ShowUsageStrategy()
