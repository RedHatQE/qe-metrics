from datetime import datetime, date, timedelta
from pyhelper_utils.general import ignore_exceptions
from typing import List
from jira import Issue
from qe_metrics.libs.database_mapping import ProductsEntity, JiraIssuesEntity
from simple_logger.logger import get_logger
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, delete

LOGGER = get_logger(name=__name__)

OBSOLETE_STR = "obsolete"


def format_issue_date(date_str: str) -> date:
    """
    Format the date in the format YYYY-MM-DD.

    Args:
        date_str (str): Date string from Jira.Issue

    Returns:
        date: Date object for database insertion
    """
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z").date()


def mark_obsolete_issues(
    current_issues: List[Issue],
    db_issues: List["JiraIssuesEntity"],
    product: "ProductsEntity",  # type: ignore  # noqa: F821
    db_session: Session,
) -> None:
    """
    Mark JiraIssuesEntity items as "obsolete" in the database that are not in the current list of issues.

    Args:
        current_issues (List[Issue]): A list of current Jira issues for a product.
        db_issues ("JiraIssuesEntity"): A list of JiraIssuesEntity objects already in the database.
        product ("ProductsEntity"): The product object to which the issues belong.
        db_session (Session): SQLAlchemy Session instance.
    """
    current_issue_keys = {issue.key for issue in current_issues}
    db_issue_keys = {db_issue.issue_key for db_issue in db_issues if db_issue.product.name == product.name}
    closed_issue_keys = db_issue_keys - current_issue_keys

    for db_issue in db_issues:
        if db_issue.issue_key in closed_issue_keys and db_issue.status != OBSOLETE_STR:
            LOGGER.info(f'Marking issue "{db_issue.issue_key}" for product {product.name} as {OBSOLETE_STR}')
            db_issue.status = OBSOLETE_STR
    db_session.commit()


def update_existing_issue(
    existing_issue: JiraIssuesEntity, new_issue_data: Issue, severity: str, db_session: Session
) -> None:
    """
    Check if any of the fields of an existing issue have changed and update them if they have.

    Args:
        existing_issue (JiraIssuesEntity): Existing issue from the database
        new_issue_data (Issue): New issue from Jira
        severity (str): Severity assigned to the issue/query
        db_session (Session): SQLAlchemy Session instance.
    """
    fields = [
        ("title", new_issue_data.fields.summary.strip()),
        ("severity", severity),
        ("status", new_issue_data.fields.status.name),
        ("issue_type", new_issue_data.fields.issuetype.name.lower()),
        ("customer_escaped", new_issue_data.is_customer_escaped),
        ("last_updated", format_issue_date(new_issue_data.fields.updated)),
    ]
    for field, new_value in fields:
        if (current_value := getattr(existing_issue, field)) != new_value:
            LOGGER.info(
                f'Updating issue "{new_issue_data.key}" in database: "{field}" changed from "{current_value}" to "{new_value}"'
            )
            setattr(existing_issue, field, new_value)
    db_session.commit()


def create_update_issues(
    issues: List[Issue], product: "ProductsEntity", severity: str, jira_server: str, db_session: Session
) -> None:
    """
    Create or update JiraIssuesEntity items in the database from a list of Jira issues. Sets status of obsolete issues as "obsolete".

    Args:
        issues (List[Issue]): A list of Jira issues
        product (ProductsEntity): A product object
        severity (str): Severity of the issues
        jira_server (str): Jira server URL
        db_session (Session): SQLAlchemy Session instance.

    Returns:
        List["JiraIssuesEntity"]: A list of JiraIssuesEntity objects
    """
    for issue in issues:
        if existing_issue := db_session.execute(
            select(JiraIssuesEntity).where(JiraIssuesEntity.issue_key == issue.key)
        ).scalar_one_or_none():
            update_existing_issue(
                existing_issue=existing_issue, new_issue_data=issue, severity=severity, db_session=db_session
            )
        else:
            db_session.execute(
                statement=insert(JiraIssuesEntity).values(
                    product_id=product.id,
                    issue_key=issue.key,
                    title=issue.fields.summary,
                    url=f"{jira_server}/browse/{issue.key}",
                    project=issue.fields.project.key,
                    severity=severity,
                    status=issue.fields.status.name,
                    issue_type=issue.fields.issuetype.name.lower(),
                    customer_escaped=issue.is_customer_escaped,
                    date_created=format_issue_date(issue.fields.created),
                    last_updated=format_issue_date(issue.fields.updated),
                )
            )

    mark_obsolete_issues(
        current_issues=issues,
        db_issues=db_session.execute(
            select(JiraIssuesEntity).where(JiraIssuesEntity.product == product, JiraIssuesEntity.severity == severity)
        ).scalars(),
        product=product,
        db_session=db_session,
    )
    db_session.commit()


@ignore_exceptions(logger=LOGGER, return_on_error=False)
def delete_old_issues(days_old: int, db_session: Session) -> bool:
    """
    Delete issues from the database that were last updated more than the number of days defined in days_old.

    Args:
        days_old (int): Number of days from the last_updated date to keep issues in the database
        db_session (Session): SQLAlchemy Session instance.
    """

    LOGGER.info(f"Deleting issues that haven't been updated in {days_old} days from the database")
    db_session.execute(
        statement=delete(JiraIssuesEntity).where(
            JiraIssuesEntity.last_updated < (datetime.now().date() - timedelta(days=days_old))
        )
    )
    db_session.commit()
    return True
