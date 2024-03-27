from __future__ import annotations
from datetime import date, datetime

from jira import Issue

from simple_logger.logger import get_logger
from typing import TYPE_CHECKING, List

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


def format_issue_date(date_str: str) -> date:
    """
    Format the date in the format YYYY-MM-DD.

    Args:
        date_str (str): Date string from Jira.Issue

    Returns:
        date: Date object for database insertion
    """
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z").date()


def update_existing_issue(existing_issue: "Database.JiraIssues", issue: Issue, severity: str) -> "Database.JiraIssues":
    """
    Check if any of the fields of an existing issue have changed and update them if they have.

    Args:
        existing_issue (Database.JiraIssues): Existing issue from the database
        issue (Issue): New issue from Jira
        severity (str): Severity assigned to the issue/query

    Returns:
        Database.JiraIssues: Updated issue object
    """
    fields = [
        ("title", issue.fields.summary.strip()),
        ("severity", severity),
        ("status", issue.fields.status.name),
        ("customer_escaped", check_customer_escaped(issue=issue)),
        ("last_updated", format_issue_date(issue.fields.updated)),
    ]
    for field, new_value in fields:
        if (current_value := getattr(existing_issue, field)) != new_value:
            LOGGER.info(
                f'Updating issue "{issue.key}" in database: "{field}" changed from "{current_value}" to "{new_value}"'
            )
            setattr(existing_issue, field, new_value)
            existing_issue.date_record_modified = datetime.now()

    return existing_issue


def delete_closed_issues(
    current_issues: List[Issue], db_issues: List["Database.JiraIssues"], product: "Database.Products"
) -> None:
    """
    Delete JiraIssues items in the database that are not in the current list of issues.

    Args:
        current_issues (List[Issue]): A list of current Jira issues for a product.
        db_issues ("Database.JiraIssues"): A list of JiraIssues objects already in the database.
        product (Database.Products): The product object to which the issues belong.
    """
    current_issue_keys = {issue.key for issue in current_issues}
    db_issue_keys = {db_issue.issue_key for db_issue in db_issues if db_issue.product.name == product.name}
    closed_issue_keys = db_issue_keys - current_issue_keys

    for db_issue in db_issues:
        if db_issue.issue_key in closed_issue_keys:
            LOGGER.info(f'Deleting closed issue "{db_issue.issue_key}" for product {product.name} from database')
            db_issue.delete()
