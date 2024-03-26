from typing import Any

import click
from jira import JIRA
from jira.exceptions import JIRAError
from pyaml_env import parse_config
from simple_logger.logger import get_logger
from qe_metrics.utils.general import verify_config


class Jira:
    def __init__(self, config_file: str) -> None:
        """
        Initialize the Jira class

        Args:
            config_file (str): Path to the yaml file holding database and Jira configuration.
        """
        self.logger = get_logger(name=self.__class__.__module__)
        self.jira_config = parse_config(config_file)["jira"]
        self._connection = None

    def __enter__(self) -> "Jira":
        self._connection = self.connection
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        if self._connection:
            self._connection.close()
            self.logger.success("Disconnected from Jira")

    @property
    def connection(self) -> JIRA:
        """
        Connect to Jira

        Returns:
            JIRA: Jira connection
        """
        if self._connection is None:
            verify_config(config=self.jira_config, required_keys=["token", "server"])
            try:
                self._connection = JIRA(server=self.jira_config["server"], token_auth=self.jira_config["token"])
                self.logger.success(f'Successfully authenticated to Jira server {self.jira_config["server"]}')
            except JIRAError as error:
                self.logger.error(f'Failed to connect to Jira server {self.jira_config["server"]}: {error}')
                raise click.Abort()

        return self._connection

    def search(self, query: str) -> list[Any]:
        """
        Performs a Jira JQL query using the Jira connection and returns a list of issues, including all fields.

        Args:
            query (str): JQL query to execute.

        Returns:
            list[Any]: List of Jira issues returned from the query.
        """
        try:
            return self.connection.search_issues(query, maxResults=False)
        except JIRAError as error:
            self.logger.error(f'Failed to execute Jira query "{query}": {error}')
            raise click.Abort()
