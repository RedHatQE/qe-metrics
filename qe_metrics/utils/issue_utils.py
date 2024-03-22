from datetime import date, datetime, timedelta

from jira import Issue


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
