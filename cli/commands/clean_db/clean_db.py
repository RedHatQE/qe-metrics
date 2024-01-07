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
from datetime import datetime
from datetime import timedelta

from pony import orm as pny
from simple_logger.logger import get_logger

from cli.obj.config import Config
from cli.obj.database import JiraIssue


class CleanDatabase:
    def __init__(self, config: Config):
        """
        Build the CleanDatabase object. This class is responsible for cleaning the database.
        Args:
            config (Config): A valid Config object
        """
        self.logger = get_logger(__name__)

        # Delete issues older than the specified number of days
        self.gather_jira_data_retention = config.gather_jira_data_retention
        self.delete_jira_issues_older_than(days=self.gather_jira_data_retention)

    @pny.db_session
    def delete_jira_issues_older_than(self, days: int) -> None:
        """
        Delete JiraIssue records that are older than the specified number of days.
        Args:
            days(int): The number of days
        Returns:
            None
        """
        self.logger.info(f"Deleting JiraIssue records older than {days} days")
        cutoff_date = datetime.now() - timedelta(days=days)

        try:
            pny.delete(j for j in JiraIssue if j.date_added < cutoff_date)  # type: ignore
        except Exception as error:
            self.logger.error(f"Failed to delete JiraIssue records: {error}")
