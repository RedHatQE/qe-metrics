# TODO: Write unit tests for the functions in this file
from __future__ import annotations
from datetime import date, datetime, timedelta

from jira import Issue

from simple_logger.logger import get_logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qe_metrics.libs.database import Database

LOGGER = get_logger(name=__name__)


def check_customer_escaped(issue: Issue) -> bool:
    """
    Check if the issue is customer escaped.

    Args:
        issue (Issue): Jira Issue

    Returns:
        bool: True if the issue is customer escaped, False otherwise.
    """
    try:
        return float(issue.fields.customfield_12313440) > 0
    except (ValueError, AttributeError):
        return False


def check_created_date(issue: Issue, days: int) -> bool:
    """
    Check if the issue was created in the last X days.

    Args:
        issue (Issue): Jira Issue
        days (int): Number of days

    Returns:
        bool: True if the issue was created in the last X days, False otherwise.
    """
    return (datetime.now().date() - format_issue_date(issue.fields.created)) <= timedelta(days=days)


def check_is_bug(issue: Issue) -> bool:
    """
    Check if the issue is a bug.

    Args:
        issue (Issue): Jira Issue

    Returns:
        bool: True if the issue is a bug, False otherwise.
    """
    return issue.fields.issuetype.name.lower() == "bug"


def format_issue_date(date_str: str) -> date:
    """
    Format the date in the format YYYY-MM-DD.

    Args:
        date_str (str): Date string from Jira.Issue

    Returns:
        date: Date object for database insertion
    """
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z").date()


def check_issue_fields_changed(
    existing_issue: "Database.JiraIssues", issue: Issue, severity: str, jira_server: str
) -> bool:
    """
    Check if any of the fields of an existing issue have changed.

    Args:
        existing_issue (Database.JiraIssues): Existing issue from the database
        issue (Issue): New issue from Jira
        severity (str): Severity assigned to the issue/query
        jira_server (str): Jira server URL

    Returns:
        bool: True if any field has changed, False otherwise
    """
    return (
        existing_issue.title.strip() != issue.fields.summary.strip()
        or existing_issue.url != f"{jira_server}/browse/{issue.key}"
        or existing_issue.project != issue.fields.project.key
        or existing_issue.severity != severity
        or existing_issue.status != issue.fields.status.name
        or existing_issue.customer_escaped != check_customer_escaped(issue=issue)
        or existing_issue.last_updated != format_issue_date(issue.fields.updated)
    )


def update_existing_issue(existing_issue: "Database.JiraIssues", issue: Issue, severity: str, jira_server: str) -> None:
    """
    Update the fields of an existing issue if they have changed.

    Args:
        existing_issue (Database.JiraIssues): Existing issue from the database
        issue (Issue): New issue from Jira
        severity (str): Severity assigned to the issue/query
        jira_server (str): Jira server URL
    """
    LOGGER.info(f'Updating issue "{issue.key}" in database')

    existing_issue.title = issue.fields.summary
    existing_issue.url = f"{jira_server}/browse/{issue.key}"
    existing_issue.project = issue.fields.project.key
    existing_issue.severity = severity
    existing_issue.status = issue.fields.status.name
    existing_issue.customer_escaped = check_customer_escaped(issue=issue)
    existing_issue.last_updated = format_issue_date(issue.fields.updated)
    existing_issue.date_record_modified = datetime.now()
