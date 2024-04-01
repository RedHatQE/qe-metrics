import os
from types import TracebackType
from typing import List, Optional, Type
from datetime import datetime


from pony import orm
from jira import Issue
from pyaml_env import parse_config
from simple_logger.logger import get_logger

from qe_metrics.utils.general import verify_config, verify_queries, format_issue_date
from qe_metrics.libs.orm_database import DB_CONNECTION, ProductsEntity, JiraIssuesEntity


LOGGER = get_logger(name="Database")


class Database:
    def __init__(self, config_file: str, verbose: bool) -> None:
        """
        Initialize the Database class

        Args:
            config_file (str): Path to the yaml file holding database and Jira configuration.
            verbose (bool): Verbose output of database connection and transactions.
        """
        self.logger = get_logger(name=self.__class__.__module__)
        orm.set_sql_debug(debug=verbose)
        self.config_file = config_file
        self.db_config = parse_config(path=self.config_file)["database"]

    def __enter__(self) -> "Database":
        self.bind_local_db_connection() if self.db_config.get("local") else self.bind_remote_db_connection()
        DB_CONNECTION.generate_mapping(create_tables=True)
        self.logger.success("Connected to the database")
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if DB_CONNECTION:
            DB_CONNECTION.disconnect()
            self.logger.success("Disconnected from the database")

    def bind_local_db_connection(self) -> None:
        """
        Bind a local database connection using SQLite.
        """
        sqlite_filepath = self.db_config.get("local_filepath", "/tmp/qe_metrics.sqlite")
        self.logger.info(f"Local database connection enabled, using SQLite database at {sqlite_filepath}")
        DB_CONNECTION.bind(provider="sqlite", filename=sqlite_filepath, create_db=not os.path.exists(sqlite_filepath))

    def bind_remote_db_connection(self) -> None:
        """
        Bind a remote database connection.
        """
        self.logger.info("Remote database connection enabled, connecting to database")
        verify_config(config=self.db_config, required_keys=["host", "user", "password", "database"])
        DB_CONNECTION.bind(
            host=self.db_config["host"],
            user=self.db_config["user"],
            password=self.db_config["password"],
            database=self.db_config["database"],
            port=self.db_config.get("port", 5432),
            provider=self.db_config.get("provider", "postgres"),
        )


def products_from_file(products_file: str) -> List["ProductsEntity"]:
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
        if not (product := ProductsEntity.get(name=name)):
            products.append(ProductsEntity(name=name, queries=queries))
        else:
            setattr(product, "queries", queries)
            products.append(product)
    orm.commit()
    return products


def update_existing_issue(existing_issue: JiraIssuesEntity, new_issue_data: Issue, severity: str) -> None:
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
        if (current_value := getattr(existing_issue, field)) != new_value:
            LOGGER.info(
                f'Updating issue "{new_issue_data.key}" in database: "{field}" changed from "{current_value}" to "{new_value}"'
            )
            setattr(existing_issue, field, new_value)
            existing_issue.date_record_modified = datetime.now()


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


def create_update_issues(
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
        if existing_issue := JiraIssuesEntity.get(issue_key=issue.key, product=product):
            update_existing_issue(existing_issue=existing_issue, new_issue_data=issue, severity=severity)
        else:
            JiraIssuesEntity(
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

    mark_stale_issues(
        current_issues=issues, db_issues=JiraIssuesEntity.select(product=product, severity=severity), product=product
    )
    orm.commit()
