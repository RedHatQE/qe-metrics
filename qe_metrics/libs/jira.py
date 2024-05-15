from typing import Any, List

import click
from jira import JIRA, Issue
from pyaml_env import parse_config
from pyhelper_utils.general import ignore_exceptions
from simple_logger.logger import get_logger
from qe_metrics.utils.general import verify_config

JIRA_CUSTOM_FIELD_MAPPING = {
    "customer_escaped": "customfield_12313440",
}
LOGGER = get_logger(name=__name__)


class Jira:
    def __init__(self, config_file: str) -> None:
        """
        Initialize the Jira class

        Args:
            config_file (str): Path to the yaml file holding database and Jira configuration.
        """
        self.jira_config = parse_config(path=config_file)["jira"]

    def __enter__(self) -> "Jira":
        self.connection = self.connect()
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        if self.connection:
            self.connection.close()
            LOGGER.success("Disconnected from Jira")

    @ignore_exceptions(retry=3, retry_interval=1, raise_final_exception=True, logger=LOGGER)
    def connect(self) -> JIRA:
        """
        Connect to Jira

        Returns:
            JIRA: Jira connection
        """
        verify_config(config=self.jira_config, required_keys=["token", "server"])
        try:
            connection = JIRA(server=self.jira_config["server"], token_auth=self.jira_config["token"])
            connection.my_permissions()
            LOGGER.success(f'Successfully authenticated to Jira server {self.jira_config["server"]}')
            return connection
        except Exception as error:
            LOGGER.error(f'Failed to connect to Jira server {self.jira_config["server"]}: {error}')
            raise click.Abort()

    @ignore_exceptions(retry=3, retry_interval=1, raise_final_exception=True, logger=LOGGER)
    def search(self, query: str) -> List[Any]:
        """
        Performs a Jira JQL query using the Jira connection and returns a list of issues, including all fields.

        Args:
            query (str): JQL query to execute.

        Returns:
            list[Any]: List of Jira issues returned from the query.
        """
        try:
            issues = self.connection.search_issues(jql_str=query, maxResults=False)
            for issue in issues:
                issue.is_customer_escaped = self.is_customer_escaped(issue=issue)
            return issues
        except Exception as error:
            LOGGER.error(f'Failed to execute Jira query "{query}": {error}')
            raise click.Abort()

    @staticmethod
    def is_customer_escaped(issue: Issue) -> bool:
        """
        Args:
            issue (Issue): Jira Issue

        Returns:
            bool: True if the issue is customer escaped, False otherwise.
        """
        try:
            return float(getattr(issue.fields, JIRA_CUSTOM_FIELD_MAPPING["customer_escaped"])) > 0
        except (TypeError, AttributeError):
            return False
