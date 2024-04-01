from qe_metrics.libs.jira import Jira

import pytest


@pytest.mark.parametrize(
    "raw_jira_issues",
    [
        [
            {
                "key": "TEST-2234",
                "title": "New Test Summary",
                "customer_escaped": "1.0",
            }
        ]
    ],
    indirect=True,
)
def test_is_customer_escaped_returns_true(raw_jira_issues):
    assert Jira.is_customer_escaped(raw_jira_issues[0]) is True


@pytest.mark.parametrize(
    "raw_jira_issues",
    [
        [
            {
                "key": "TEST-2235",
                "title": "New Test Summary",
            }
        ]
    ],
    indirect=True,
)
def test_is_customer_escaped_returns_false(raw_jira_issues):
    assert Jira.is_customer_escaped(raw_jira_issues[0]) is False
