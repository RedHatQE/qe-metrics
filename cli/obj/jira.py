#
# Copyright (C) 2024 Red Hat, Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from typing import Any

from jira import JIRA
from jira.exceptions import JIRAError
from simple_logger.logger import get_logger


class Jira:
    def __init__(self, token: str, server: str) -> None:
        """
        Initializes the Jira object and attempts to connect to the Jira server.
        Args:
            token (str): Jira API token.
            server (str): Jira server URL.
        Returns:
            None
        """
        self.logger = get_logger(__name__)

        self.connection = self._connect(token=token, server=server)

    def _connect(self, token: str, server: str) -> JIRA:
        """
        Attempts to connect to the Jira server using the provided token and server URL.
        Args:
            token (str): Jira API token.
            server (str): Jira server URL.
        Returns:
            JIRA: Jira connection object.
        """
        self.logger.info("Attempting to connect to Jira")
        try:
            connection = JIRA(
                server=server,
                token_auth=token,
            )
            self.logger.info("Jira authentication successful")
            return connection
        except JIRAError:
            self.logger.error("Jira authentication failed")
            exit(1)

    def search(self, jql_query: str) -> list[Any]:
        """
        Performs a Jira JQL query using the Jira connection and returns a list of issues, including all fields.

        Args:
            jql_query (str): JQL query to run.

        Returns:
            list[Any]: List of issues that are returned from the query.
        """
        return self.connection.search_issues(jql_query, validate_query=True)
