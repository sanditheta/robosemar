import yaml
from typing import Dict

class Config:
    def __init__(self, config_path: str = "config/config.yaml"):
        with open(config_path, 'r') as file:
            self.config: Dict[str, any] = yaml.safe_load(file)

    def get(self, key: str, default=None):
        return self.config.get(key, default)
