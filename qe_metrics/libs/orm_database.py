from pony import orm
from datetime import date, datetime

from jira import Issue
from simple_logger.logger import get_logger
from typing import List, Any

from pyaml_env import parse_config

from qe_metrics.utils.general import verify_queries
from qe_metrics.utils.general import format_issue_date

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

    @classmethod
    def create_update_issues(
        cls,
        issues: List[Issue],
        product: "ProductsEntity",
        severity: str,
        jira_server: str,  # type: ignore  # noqa: F821
    ) -> None:
        """
        Create or update JiraIssuesEntity items in the database from a list of Jira issues.

        Args:
            issues (List[Issue]): A list of Jira issues
            product (ProductsEntity): A product object
            severity (str): Severity of the issues
            jira_server (str): Jira server URL

        Returns:
            List["JiraIssuesEntity"]: A list of JiraIssuesEntity objects
        """
        issues = [_issue for _issue in issues if _issue.fields.issuetype.name.lower() == "bug"]
        for issue in issues:
            if existing_issue := cls.get(issue_key=issue.key, product=product):
                existing_issue.update_existing_issue(new_issue_data=issue, severity=severity)
            else:
                cls(
                    product=product,
                    issue_key=issue.key,
                    title=issue.fields.summary,
                    url=f"{jira_server}/browse/{issue.key}",
                    project=issue.fields.project.key,
                    severity=severity,
                    status=issue.fields.status.name,
                    customer_escaped=issue.is_customer_escaped,
                    date_created=format_issue_date(issue.fields.created),
                    last_updated=format_issue_date(issue.fields.updated),
                )

        cls.mark_stale_issues(
            current_issues=issues, db_issues=cls.select(product=product, severity=severity), product=product
        )
        orm.commit()

    def update_existing_issue(self, new_issue_data: Issue, severity: str) -> None:
        """
        Check if any of the fields of an existing issue have changed and update them if they have.

        Args:
            existing_issue (JiraIssuesEntity): Existing issue from the database
            issue (Issue): New issue from Jira
            severity (str): Severity assigned to the issue/query
        """
        fields = [
            ("title", new_issue_data.fields.summary.strip()),
            ("severity", severity),
            ("status", new_issue_data.fields.status.name),
            ("customer_escaped", new_issue_data.is_customer_escaped),
            ("last_updated", format_issue_date(new_issue_data.fields.updated)),
        ]
        for field, new_value in fields:
            if (current_value := getattr(self, field)) != new_value:
                self.logger.info(
                    f'Updating issue "{new_issue_data.key}" in database: "{field}" changed from "{current_value}" to "{new_value}"'
                )
                setattr(self, field, new_value)
                self.date_record_modified = datetime.now()

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

    @classmethod
    def from_file(cls, products_file: str) -> List["ProductsEntity"]:
        """
        Initialize the ProductsEntity class from a file. Create new entries if they do not exist. Update the queries if
        they are modified.

        Args:
            products_file (str): Path to the yaml file holding product names and their queries

        Returns:
            List["ProductsEntity"]: A list of Products objects
        """
        products_dict = parse_config(path=products_file)
        products = []
        for name, queries in products_dict.items():
            verify_queries(queries_dict=queries)
            if not (product := cls.get(name=name)):
                products.append(cls(name=name, queries=queries))
            else:
                setattr(product, "queries", queries)
                products.append(product)
        orm.commit()
        return products
