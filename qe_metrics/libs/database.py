import os
from types import TracebackType
from typing import Optional, Type


from pony import orm
from pyaml_env import parse_config
from simple_logger.logger import get_logger

from qe_metrics.utils.general import verify_config
from qe_metrics.libs.orm_database import DB_CONNECTION


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
