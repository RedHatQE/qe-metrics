from datetime import date
from qe_metrics.utils.issue_utils import (
    check_customer_escaped,
    format_issue_date,
    update_existing_issue,
    delete_stale_issues,
)

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
def test_check_customer_escaped_returns_true(raw_jira_issues):
    assert check_customer_escaped(raw_jira_issues[0]) is True


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
def test_check_customer_escaped_returns_false(raw_jira_issues):
    assert check_customer_escaped(raw_jira_issues[0]) is False


@pytest.mark.parametrize(
    "product, raw_jira_issues, jira_issues",
    [
        pytest.param(
            (
                "update-existing-issue-product",
                {"blocker": "BLOCKER QUERY", "critical-blocker": "CRITICAL BLOCKER QUERY"},
            ),
            [
                {
                    "key": "TEST-1234",
                    "title": "New Test Summary",
                    "status": "In Progress",
                    "customer_escaped": "0.0",
                    "last_updated": "2023-12-31T23:59:59.999999+0000",
                }
            ],
            [
                {
                    "issue_key": "TEST-1234",
                    "title": "Test Summary",
                    "url": "https://jira.com",
                    "project": "TEST",
                    "severity": "blocker",
                    "status": "To Do",
                    "customer_escaped": True,
                    "date_created": "2024-12-29",
                    "last_updated": "2024-12-30",
                }
            ],
        ),
    ],
    indirect=True,
)
def test_update_existing_issue(product, raw_jira_issues, jira_issues):
    updated_issue = update_existing_issue(jira_issues[0], raw_jira_issues[0], "critical")
    expected_values = {
        "title": "New Test Summary",
        "severity": "critical",
        "status": "In Progress",
        "customer_escaped": False,
        "last_updated": date(2023, 12, 31),
    }
    actual_values = {
        "title": updated_issue.title,
        "severity": updated_issue.severity,
        "status": updated_issue.status,
        "customer_escaped": updated_issue.customer_escaped,
        "last_updated": updated_issue.last_updated,
    }
    assert actual_values == expected_values, f"{actual_values} != {expected_values}"


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
def test_format_issue_date(raw_jira_issues):
    assert format_issue_date(raw_jira_issues[0].fields.updated) == date(2023, 12, 31)


@pytest.mark.parametrize(
    "product, raw_jira_issues, jira_issues",
    [
        pytest.param(
            ("delete-stale-issues-product", {"blocker": "BLOCKER QUERY", "critical-blocker": "CRITICAL BLOCKER QUERY"}),
            [
                {
                    "key": "TEST-1234",
                    "title": "Test Summary",
                    "status": "In Progress",
                    "customer_escaped": "0.0",
                    "last_updated": "2023-12-31T23:59:59.999999+0000",
                },
                {
                    "key": "TEST-1236",
                    "title": "Test Summary",
                    "status": "In Progress",
                    "customer_escaped": "0.0",
                    "last_updated": "2023-12-31T23:59:59.999999+0000",
                },
            ],
            [
                {
                    "issue_key": "TEST-1234",
                    "title": "Test Summary",
                    "url": "https://jira.com",
                    "project": "TEST",
                    "severity": "blocker",
                    "status": "In Progress",
                    "customer_escaped": False,
                    "date_created": "2024-12-30",
                    "last_updated": "2024-12-31",
                },
                {
                    "issue_key": "TEST-1235",
                    "title": "Test Summary",
                    "url": "https://jira.com",
                    "project": "TEST",
                    "severity": "blocker",
                    "status": "In Progress",
                    "customer_escaped": False,
                    "date_created": "2024-12-30",
                    "last_updated": "2024-12-31",
                },
            ],
        ),
    ],
    indirect=True,
)
def test_delete_stale_issues(tmp_sqlite_db, product, raw_jira_issues, jira_issues):
    delete_stale_issues(current_issues=raw_jira_issues, db_issues=jira_issues, product=product)
    for issue in tmp_sqlite_db.JiraIssues.select():
        assert issue.issue_key != "TEST-1235"
