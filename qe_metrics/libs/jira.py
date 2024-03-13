from typing import Any
import re

import click
from jira import JIRA
from jira.exceptions import JIRAError
from pyaml_env import parse_config
from simple_logger.logger import get_logger
from qe_metrics.utils.general import verify_creds


class Jira:
    def __init__(self, creds_file: str) -> None:
        """
        Initialize the Jira class

        Args:
            creds_file (str): Path to the yaml file holding database and Jira credentials.
        """
        self.logger = get_logger(name=self.__class__.__module__)

        self.jira_creds = parse_config(creds_file)["jira"]

    @property
    def connection(self) -> JIRA:
        """
        Connect to Jira

        Returns:
            JIRA: Jira connection
        """
        verify_creds(creds=self.jira_creds, required_keys=["token", "server"])
        try:
            connection = JIRA(server=self._force_https(self.jira_creds["server"]), token_auth=self.jira_creds["token"])
            self.logger.success(f'Successfully authenticated to Jira server {self.jira_creds["server"]}')
            return connection
        except JIRAError as error:
            self.logger.error(f'Failed to connect to Jira server {self.jira_creds["server"]}: {error}')
            raise click.Abort()

    @staticmethod
    def _force_https(server: str) -> str:
        """
        Force the server URL to use HTTPS

        Args:
            server (str): Jira server URL

        Returns:
            str: Jira server URL with "https://" prefix
        """
        return re.sub(r"^(http://)?(https://)?", "https://", server)

    def search(self, query: str) -> list[Any]:
        """
        Performs a Jira JQL query using the Jira connection and returns a list of issues, including all fields.

        Args:
            query (str): JQL query to execute.

        Returns:
            list[Any]: List of Jira issues returned from the query.
        """
        try:
            return self.connection.search_issues(query, maxResults=False, validate_query=True)
        except JIRAError as error:
            self.logger.error(f"Failed to execute Jira query: {error}")
            raise click.Abort()
