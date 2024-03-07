import os
from datetime import date
from pony import orm as pny
from pyaml_env import parse_config
from simple_logger.logger import get_logger

DB_CONNECTION = pny.Database()
DEFAULT_SQLITE_DB_FILEPATH = "/tmp/qe_metrics.sqlite"


class Database:
    def __init__(self, creds_file: str, verbose: bool) -> None:
        """
        Initialize the Database class

        Args:
            creds_file (str): Path to the yaml file holding database and Jira credentials.
            verbose (bool): Verbose output of database connection and transactions.
        """
        self.logger = get_logger(name=self.__class__.__module__)
        pny.set_sql_debug(verbose)  # Set verbose database connection if requested

        self.db_creds = parse_config(creds_file)["database"]
        self.connection = DB_CONNECTION

        if self.db_creds.get("local"):
            sqlite_filepath = (
                DEFAULT_SQLITE_DB_FILEPATH
                if not self.db_creds.get("local_filepath")
                else self.db_creds.get("local_filepath")
            )
            self.logger.info(f"Local database connection enabled, using SQLite database at {sqlite_filepath}")
            self.connection.bind(
                provider="sqlite", filename=sqlite_filepath, create_db=not os.path.exists(sqlite_filepath)
            )
        else:
            self.logger.info("Remote database connection enabled, connecting to database")
            self.connection.bind(
                provider=self.db_creds.get("provider", "postgres"),
                host=self.db_creds.get("host"),
                user=self.db_creds.get("user"),
                password=self.db_creds.get("password"),
                database=self.db_creds.get("database"),
                port=self.db_creds.get("port", 5432),
            )

        self.connection.generate_mapping(create_tables=True)

    def __del__(self) -> None:
        """
        Destructor method to disconnect from the database when the object is about to be destroyed.
        """
        if self.connection:
            self.connection.disconnect()
            self.logger.info("Disconnected from the database")


class Services(DB_CONNECTION.Entity):  # type: ignore
    """
    A class to represent the Services table in the database.
    """

    id = pny.PrimaryKey(int, auto=True)
    name = pny.Required(str)
    jira_issues = pny.Set("JiraIssues")


class JiraIssues(DB_CONNECTION.Entity):  # type: ignore
    """
    A class to represent the JiraIssues table in the database.
    """

    id = pny.PrimaryKey(int, auto=True)
    service = pny.Required(Services)
    issue_key = pny.Required(str)
    title = pny.Required(str)
    url = pny.Required(str)
    project = pny.Required(str)
    severity = pny.Required(str)
    status = pny.Required(str)
    customer_escaped = pny.Required(bool)
    date_created = pny.Required(date)
    last_updated = pny.Required(date)
