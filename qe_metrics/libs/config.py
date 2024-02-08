from pyaml_env import parse_config
from simple_logger.logger import get_logger


class Config:
    def __init__(self, config_file: str) -> None:
        """
        Initialize the Config class
        Args:
            config_file (str): Path to the yaml config file.
        """
        self.logger = get_logger(name=self.__class__.__module__)
        self.config = parse_config(config_file)

        # TODO: Add database connection
        # TODO: Add Jira connection
        # TODO: Validate queries given in the config file
