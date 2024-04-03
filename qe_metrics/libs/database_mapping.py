from pony import orm
from datetime import date, datetime

from jira import Issue
from simple_logger.logger import get_logger
from typing import Any


DB_OBJECT: orm.Database = orm.Database()


class JiraIssuesEntity(DB_OBJECT.Entity):
    """
    A class to represent the JiraIssues table in the database.
    """

    _table_ = "jiraissues"

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


class ProductsEntity(DB_OBJECT.Entity):
    """
    A class to represent the Products table in the database.
    """

    _table_ = "products"

    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str, unique=True)
    jira_issues = orm.Set("JiraIssuesEntity")

    def __init__(self, queries: dict[str, str], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.queries = queries
