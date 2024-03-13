import os
from types import TracebackType
from typing import Optional, Type

from datetime import date
from pony import orm
from pyaml_env import parse_config
from simple_logger.logger import get_logger
from qe_metrics.utils.general import verify_creds

DB_CONNECTION = orm.Database()


class Database:
    def __init__(self, creds_file: str, verbose: bool) -> None:
        """
        Initialize the Database class

        Args:
            creds_file (str): Path to the yaml file holding database and Jira credentials.
            verbose (bool): Verbose output of database connection and transactions.
        """
        self.logger = get_logger(name=self.__class__.__module__)
        orm.set_sql_debug(verbose)

        self.creds_file = creds_file
        self.db_creds = parse_config(self.creds_file)["database"]
        self.connection = DB_CONNECTION

        if self.db_creds.get("local"):
            self.bind_local_db_connection()
        else:
            self.bind_remote_db_connection()

        self.connection.generate_mapping(create_tables=True)

    def __enter__(self) -> "Database":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self.connection:
            self.connection.disconnect()
            self.logger.info("Disconnected from the database")

    def bind_local_db_connection(self) -> None:
        """
        Bind a local database connection using SQLite.
        """
        sqlite_filepath = self.db_creds.get("local_filepath", "/tmp/qe_metrics.sqlite")
        self.logger.info(f"Local database connection enabled, using SQLite database at {sqlite_filepath}")
        self.connection.bind(provider="sqlite", filename=sqlite_filepath, create_db=not os.path.exists(sqlite_filepath))

    def bind_remote_db_connection(self) -> None:
        """
        Bind a remote database connection.
        """
        self.logger.info("Remote database connection enabled, connecting to database")
        verify_creds(creds=self.db_creds, required_keys=["host", "user", "password", "database"])
        self.connection.bind(
            host=self.db_creds["host"],
            user=self.db_creds["user"],
            password=self.db_creds["password"],
            database=self.db_creds["database"],
            port=self.db_creds.get("port", 5432),
            provider=self.db_creds.get("provider", "postgres"),
        )

    class Services(DB_CONNECTION.Entity):  # type: ignore
        """
        A class to represent the Services table in the database.
        """

        id = orm.PrimaryKey(int, auto=True)
        name = orm.Required(str, unique=True)
        jira_issues = orm.Set("JiraIssues")

    class JiraIssues(DB_CONNECTION.Entity):  # type: ignore
        """
        A class to represent the JiraIssues table in the database.
        """

        id = orm.PrimaryKey(int, auto=True)
        service = orm.Required("Services")
        issue_key = orm.Required(str, unique=True)
        title = orm.Required(str)
        url = orm.Required(str)
        project = orm.Required(str)
        severity = orm.Required(str)
        status = orm.Required(str)
        customer_escaped = orm.Required(bool)
        date_created = orm.Required(date)
        last_updated = orm.Required(date)
