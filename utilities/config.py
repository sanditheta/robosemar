import yaml
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class ConfigurationManager(metaclass=SingletonMeta):
    def __init__(self, config_file="config/config.yaml"):
        self._config = None
        self._config_file = config_file

    def load(self):
        if self._config is None:
            try:
                with open(self._config_file, "r") as file:
                    self._config = yaml.safe_load(file)
                logger.info(f"Configuration loaded from {self._config_file}")
            except FileNotFoundError:
                logger.error(f"Configuration file {self._config_file} not found")
                raise
            except yaml.YAMLError as exc:
                logger.error(
                    f"Error parsing the configuration file {self._config_file}"
                )
                raise

    def get(self, key: str, default=None):
        # Implementing lazy loading
        if self._config is None:
            self.load()
        return self._config.get(key, default)

    def update(self, key: str, value):
        # Adding dynamic update functionality
        if self._config is None:
            self.load()
        self._config[key] = value
