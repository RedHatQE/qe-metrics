from abc import ABC

from pyaml_env import parse_config
from simple_logger.logger import get_logger


class QeMetricsBase(ABC):
    def __init__(self, creds_file: str) -> None:
        """
        Initialize the QeMetricsBase class
        Args:
            creds_file (str): Path to the yaml file holding database and Jira credentials.
        """
        self.logger = get_logger(name=self.__class__.__module__)

        # Creds dict will hold credentials to Jira and the database (and any other future service)
        self.creds_dict = parse_config(creds_file)

        # TODO: Define and validate configuration values from the config and creds files to be used in subclasses
