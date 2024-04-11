from pony import orm
from datetime import date


DB_OBJECT: orm.Database = orm.Database()


class JiraIssuesEntity(DB_OBJECT.Entity):
    """
    A class to represent the JiraIssues table in the database.
    """

    _table_ = "jiraissues"

    id = orm.PrimaryKey(int, auto=True)
    product = orm.Required("ProductsEntity")
    issue_key = orm.Required(str)
    title = orm.Required(str)
    url = orm.Required(str)
    project = orm.Required(str)
    severity = orm.Required(str)
    status = orm.Required(str)
    issue_type = orm.Required(str)
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
