from typing import Dict, Any

from simple_logger.logger import get_logger


class UserInput:
    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """
        Initialize the UserInput class.

        Args:
            **kwargs (Dict[str, Any]): Keyword arguments from CLI.
        """

        self.logger = get_logger(name=self.__class__.__module__)
        self.config_path = str(kwargs.get("config"))
        self.local_db = kwargs.get("local_db")
        self.verbose = kwargs.get("verbose")
