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
import unittest

import pytest

from cli.obj.gather_jira_rule import GatherJiraRule


class TestGatherJiraRule(unittest.TestCase):
    def setUp(self):
        self.rule_dict = {
            "classification": "test",
            "query": "project = QE AND issuetype = Bug AND status = Open",
        }

    def test_get_rule_classification(self):
        gather_jira_rule = GatherJiraRule(rule_dict=self.rule_dict)
        self.assertEqual(gather_jira_rule.classification, "test")

    def test_get_rule_query(self):
        gather_jira_rule = GatherJiraRule(rule_dict=self.rule_dict)
        self.assertEqual(
            gather_jira_rule.query,
            "project = QE AND issuetype = Bug AND status = Open",
        )

    def test_get_rule_classification_missing(self):
        self.rule_dict.pop("classification")
        with pytest.raises(SystemExit):
            GatherJiraRule(rule_dict=self.rule_dict)

    def test_get_rule_classification_not_string(self):
        self.rule_dict["classification"] = 1
        with pytest.raises(SystemExit):
            GatherJiraRule(rule_dict=self.rule_dict)

    def test_get_rule_query_missing(self):
        self.rule_dict.pop("query")
        with pytest.raises(SystemExit):
            GatherJiraRule(rule_dict=self.rule_dict)

    def test_get_rule_query_not_string(self):
        self.rule_dict["query"] = 1
        with pytest.raises(SystemExit):
            GatherJiraRule(rule_dict=self.rule_dict)
