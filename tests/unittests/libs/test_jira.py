from qe_metrics.libs.jira import Jira

import pytest


@pytest.mark.parametrize(
    "raw_jira_issues",
    [
        [
            {
                "key": "TEST-1234",
                "title": "New Test Summary",
                "status": "In Progress",
                "customer_escaped": "1.0",
                "last_updated": "2023-12-31T23:59:59.999999+0000",
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
                "key": "TEST-1234",
                "title": "New Test Summary",
                "status": "In Progress",
                "customer_escaped": "0.0",
                "last_updated": "2023-12-31T23:59:59.999999+0000",
            }
        ]
    ],
    indirect=True,
)
def test_is_customer_escaped_returns_false(raw_jira_issues):
    assert Jira.is_customer_escaped(raw_jira_issues[0]) is False
