import logging
from typing import List, Tuple
from components.cli import CLI
from components.runner import (
    StrategyRunner,
    initialize_components,
    select_strategy
)
from utilities.config import ConfigurationManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    config_manager = ConfigurationManager("config/config.yaml")

    _, recorder, vad = initialize_components(config_manager)

    args = CLI.parse_args()  # Assuming CLI is available in this context

    strategy = select_strategy(args, recorder, vad)

    runner = StrategyRunner(strategy)
    runner.run()


if __name__ == "__main__":
    main()
