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

from simple_logger.logger import get_logger


class GatherJiraRule:
    def __init__(self, rule_dict: dict[Any, Any]) -> None:
        """
        Initialize the GatherJiraRule object.
        Args:
            rule_dict (dict): Dictionary containing the rule values.
        Returns:
            None
        """
        self.logger = get_logger(__name__)

        # Define the rule classification
        self.classification = self._get_rule_classification(rule_dict=rule_dict)

        # Define the rule JQL query
        self.query = self._get_rule_query(rule_dict=rule_dict)

    def _get_rule_classification(self, rule_dict: dict[Any, Any]) -> str:
        """
        Get the rule classification from the rule dictionary.
        Args:
            rule_dict (dict): Dictionary containing the rule values.
        Returns:
            str: The rule classification.
        """
        classification = rule_dict.get("classification")

        # Check if the classification value is defined
        if not classification:
            self.logger.error(
                f"Classification value is required in rule values. Offending rule: {rule_dict}",
            )
            exit(1)

        # Check if the classification value is a string
        if not isinstance(classification, str):
            self.logger.error(
                f"Classification value must be a string. Offending rule: {rule_dict}",
            )
            exit(1)

        return classification.lower()

    def _get_rule_query(self, rule_dict: dict[Any, Any]) -> str:
        """
        Get the rule JQL query from the rule dictionary.
        Args:
            rule_dict (dict): Dictionary containing the rule values.
        Returns:
            str: The rule JQL query.
        """
        query = rule_dict.get("query")

        # Check if the query value is defined
        if not query:
            self.logger.error(
                f"Query value is required in rule values. Offending rule: {rule_dict}",
            )
            exit(1)

        # Check if the query value is a string
        if not isinstance(query, str):
            self.logger.error(
                f"Query value must be a string. Offending rule: {rule_dict}",
            )
            exit(1)

        return query
