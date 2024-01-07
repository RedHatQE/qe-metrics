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
from typing import Any

from pony import orm as pny
from simple_logger.logger import get_logger

from cli.obj.config import Config
from cli.obj.database import JiraIssue
from cli.obj.database import Team
from cli.obj.gather_jira_rule import GatherJiraRule


class GatherJira:
    @pny.db_session
    def __init__(self, config: Config) -> None:
        """
        Builds the GatherJira object. This class is responsible for gathering data and inserting it into the database.

        Args:
            config (Config): A valid Config object
        """
        self.logger = get_logger(__name__)

        # Define values for jira and database
        self.jira = config.jira
        self.database = config.database
        self.jira_server = config.jira_server

        # Define values for gather_jira
        self.gather_jira_data_retention = config.gather_jira_data_retention
        self.gather_jira_team = config.gather_jira_team
        self.gather_jira_rules = config.gather_jira_rules

        # Find issues
        self.rule_issue_pairs = self._find_issues(rules=self.gather_jira_rules)

        # Insert issues to database
        self._insert_issues(rule_issue_pairs=self.rule_issue_pairs)

    def _find_issues(self, rules: list[GatherJiraRule]) -> list[dict[Any, Any]]:
        """
        Executes the Jira queries in the rules and returns a list of dictionaries containing the rule and the issues.
        Args:
            rules (list[GatherJiraRule]): A list of GatherJiraRule objects
        Returns:
            list[dict[Any, Any]]: A list of dictionaries containing the rule and the issues
        """
        rule_issue_pairs = []

        # Search for issues for each rule
        self.logger.info("Searching for issues")
        for rule in rules:
            issues = self.jira.search(jql_query=rule.query)
            rule_issue_pairs.append({"rule": rule, "issues": issues})

        return rule_issue_pairs

    @pny.db_session
    def _insert_issues(self, rule_issue_pairs: list[dict[Any, Any]]) -> None:
        """
        Uses the rule_issue_pairs to insert issues into the database.
        Args:
            rule_issue_pairs (list[dict[Any, Any]]): A list of dictionaries containing the rule and the issues
        Returns:
            None
        """
        self.logger.info("Inserting issues into database")
        for pair in rule_issue_pairs:
            rule = pair["rule"]
            issues = pair["issues"]

            for issue in issues:
                team = Team.get(name=self.gather_jira_team)
                JiraIssue(
                    team=team,
                    classification=rule.classification,
                    issue_key=issue.key,
                    link=f"{self.jira_server}/browse/{issue.key}",
                    date_created=datetime.strptime(
                        issue.fields.created.split("T")[0],
                        "%Y-%m-%d",
                    ),
                    last_updated=datetime.strptime(
                        issue.fields.updated.split("T")[0],
                        "%Y-%m-%d",
                    ),
                    assignee=issue.fields.assignee.name
                    if issue.fields.assignee
                    else "",
                    reporter=issue.fields.reporter.name
                    if issue.fields.reporter
                    else "",
                    status=issue.fields.status.name,
                    priority=issue.fields.priority.name,
                    components=str(issue.fields.components),
                    affects_versions=str(issue.fields.versions),
                    labels=str(issue.fields.labels),
                )
        # Commit changes to database
        self.logger.info("Committing changes to database")
        pny.commit()
