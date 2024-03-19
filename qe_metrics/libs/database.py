import os
from types import TracebackType
from typing import Optional, Type, List

from datetime import date
from pony import orm
from pyaml_env import parse_config
from simple_logger.logger import get_logger

from qe_metrics.utils.general import verify_config


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
            self.logger.info("Disconnected from the database")

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

    class Services(DB_CONNECTION.Entity):  # type: ignore
        """
        A class to represent the Services table in the database.
        """

        id = orm.PrimaryKey(int, auto=True)
        name = orm.Required(str, unique=True)
        jira_issues = orm.Set("JiraIssues")
        queries = orm.Required(orm.Json)

        @classmethod
        @orm.db_session
        def from_file(cls, services_file: str) -> List["Database.Services"]:
            """
            Initialize the Service class from a file. Create new entries if they do not exist. Update the queries if
            they are modified.

            Args:
                services_file (str): Path to the yaml file holding service names and their queries

            Returns:
                List["Database.Services"]: A list of Service objects
            """
            services_dict = parse_config(services_file)
            services = [
                cls(name=name, queries=queries)
                if not (service := cls.get(name=name))
                else (setattr(service, "queries", queries) or service)  # type: ignore
                for name, queries in services_dict.items()
            ]
            orm.commit()
            return services

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
