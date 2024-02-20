from pyaml_env import parse_config
from simple_logger.logger import get_logger


class Database:
    def __init__(self, creds_file: str) -> None:
        """
        Initialize the Database class

        Args:
            creds_file (str): Path to the yaml file holding database and Jira credentials.

        """
        self.logger = get_logger(name=self.__class__.__module__)

        self.creds_dict = parse_config(creds_file)

        # TODO: Add database connection


# TODO: Define database schema here
