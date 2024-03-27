import os
from types import TracebackType
from typing import Optional, Type, List, Any

from datetime import date, datetime

from jira import Issue
from pony import orm
from pyaml_env import parse_config
from simple_logger.logger import get_logger

from qe_metrics.utils.general import verify_config, verify_queries
from qe_metrics.utils.issue_utils import (
    check_customer_escaped,
    format_issue_date,
    update_existing_issue,
    delete_closed_issues,
)


class Database:
    DB_CONNECTION = orm.Database()

    def __init__(self, config_file: str, verbose: bool) -> None:
        """
        Initialize the Database class

        Args:
            config_file (str): Path to the yaml file holding database and Jira configuration.
            verbose (bool): Verbose output of database connection and transactions.
        """
        self.logger = get_logger(name=self.__class__.__module__)
        orm.set_sql_debug(verbose)

        self.config_file = config_file
        self.db_config = parse_config(self.config_file)["database"]
        self.bind_local_db_connection() if self.db_config.get("local") else self.bind_remote_db_connection()
        self.DB_CONNECTION.generate_mapping(create_tables=True)

    def __enter__(self) -> "Database":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self.DB_CONNECTION:
            self.DB_CONNECTION.disconnect()
            self.logger.success("Disconnected from the database")

    def bind_local_db_connection(self) -> None:
        """
        Bind a local database connection using SQLite.
        """
        sqlite_filepath = self.db_config.get("local_filepath", "/tmp/qe_metrics.sqlite")
        self.logger.info(f"Local database connection enabled, using SQLite database at {sqlite_filepath}")
        self.DB_CONNECTION.bind(
            provider="sqlite", filename=sqlite_filepath, create_db=not os.path.exists(sqlite_filepath)
        )

    def bind_remote_db_connection(self) -> None:
        """
        Bind a remote database connection.
        """
        self.logger.info("Remote database connection enabled, connecting to database")
        verify_config(config=self.db_config, required_keys=["host", "user", "password", "database"])
        self.DB_CONNECTION.bind(
            host=self.db_config["host"],
            user=self.db_config["user"],
            password=self.db_config["password"],
            database=self.db_config["database"],
            port=self.db_config.get("port", 5432),
            provider=self.db_config.get("provider", "postgres"),
        )

    class Products(DB_CONNECTION.Entity):  # type: ignore
        """
        A class to represent the Products table in the database.
        """

        id = orm.PrimaryKey(int, auto=True)
        name = orm.Required(str, unique=True)
        jira_issues = orm.Set("JiraIssues")

        def __init__(self, queries: dict[str, str], **kwargs: Any) -> None:
            """
            Initialize the Products class.

            Args:
                queries (dict): A dictionary of queries
            """
            super().__init__(**kwargs)
            self.queries = queries

        @classmethod
        def from_file(cls, products_file: str) -> List["Database.Products"]:
            """
            Initialize the Products class from a file. Create new entries if they do not exist. Update the queries if
            they are modified.

            Args:
                products_file (str): Path to the yaml file holding product names and their queries

            Returns:
                List["Database.Products"]: A list of Products objects
            """
            products_dict = parse_config(products_file)
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

    class JiraIssues(DB_CONNECTION.Entity):  # type: ignore
        """
        A class to represent the JiraIssues table in the database.
        """

        id = orm.PrimaryKey(int, auto=True)
        product = orm.Required("Products")
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
            cls, issues: List[Issue], product: "Database.Products", severity: str, jira_server: str
        ) -> None:
            """
            Create or update JiraIssues items in the database from a list of Jira issues.

            Args:
                issues (List[Issue]): A list of Jira issues
                product (Database.Products): A product object
                severity (str): Severity of the issues
                jira_server (str): Jira server URL

            Returns:
                List["Database.JiraIssues"]: A list of JiraIssues objects
            """
            issues = [_issue for _issue in issues if _issue.fields.issuetype.name.lower() == "bug"]
            for issue in issues:
                existing_issue = cls.get(issue_key=issue.key, product=product)
                if existing_issue:
                    update_existing_issue(existing_issue, issue, severity)
                else:
                    cls(
                        product=product,
                        issue_key=issue.key,
                        title=issue.fields.summary,
                        url=f"{jira_server}/browse/{issue.key}",
                        project=issue.fields.project.key,
                        severity=severity,
                        status=issue.fields.status.name,
                        customer_escaped=check_customer_escaped(issue=issue),
                        date_created=format_issue_date(issue.fields.created),
                        last_updated=format_issue_date(issue.fields.updated),
                    )

            delete_closed_issues(
                current_issues=issues, db_issues=cls.select(product=product, severity=severity), product=product
            )
            orm.commit()
