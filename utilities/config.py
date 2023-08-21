import yaml
from typing import Dict


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class ConfigurationManager(metaclass=SingletonMeta):
    def __init__(self, config_path: str):
        with open(config_path, "r") as file:
            self.config: Dict[str, any] = yaml.safe_load(file)

    def get(self, key: str, default=None):
        return self.config.get(key, default)
