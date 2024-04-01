from pony import orm
from datetime import date, datetime

from jira import Issue
from simple_logger.logger import get_logger
from typing import List, Any


DB_CONNECTION: orm.Database = orm.Database()


class JiraIssuesEntity(DB_CONNECTION.Entity):
    """
    A class to represent the JiraIssues table in the database.
    """

    _table_ = "JiraIssues"

    logger = get_logger(name=__module__)

    id = orm.PrimaryKey(int, auto=True)
    product = orm.Required("ProductsEntity")
    issue_key = orm.Required(str)
    title = orm.Required(str)
    url = orm.Required(str)
    project = orm.Required(str)
    severity = orm.Required(str)
    status = orm.Required(str)
    customer_escaped = orm.Required(bool)
    date_created = orm.Required(date)
    last_updated = orm.Required(date)
    date_record_modified = orm.Required(datetime, default=datetime.now)

    @staticmethod
    def mark_stale_issues(
        current_issues: List[Issue],
        db_issues: List["JiraIssuesEntity"],
        product: "ProductsEntity",  # type: ignore  # noqa: F821
    ) -> None:
        """
        Mark JiraIssuesEntity items as "stale" in the database that are not in the current list of issues.

        Args:
            current_issues (List[Issue]): A list of current Jira issues for a product.
            db_issues ("JiraIssuesEntity"): A list of JiraIssuesEntity objects already in the database.
            product ("ProductsEntity"): The product object to which the issues belong.
        """
        current_issue_keys = {issue.key for issue in current_issues}
        db_issue_keys = {db_issue.issue_key for db_issue in db_issues if db_issue.product.name == product.name}
        closed_issue_keys = db_issue_keys - current_issue_keys

        for db_issue in db_issues:
            if db_issue.issue_key in closed_issue_keys and db_issue.status != "stale":
                db_issue.logger.info(f'Marking issue "{db_issue.issue_key}" for product {product.name} as stale')
                db_issue.status = "stale"


class ProductsEntity(DB_CONNECTION.Entity):
    """
    A class to represent the Products table in the database.
    """

    _table_ = "Products"

    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str, unique=True)
    jira_issues = orm.Set("JiraIssuesEntity")

    def __init__(self, queries: dict[str, str], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.queries = queries
