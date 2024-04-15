from types import TracebackType
from typing import Any, Dict, Optional, Type

from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, scoped_session
from pyaml_env import parse_config
from simple_logger.logger import get_logger

from qe_metrics.utils.general import verify_config
from qe_metrics.libs.database_mapping import Base


class Database:
    def __init__(self, config_file: str, verbose: bool) -> None:
        self.logger = get_logger(name=__name__)
        self.connection_string = self.connection_string_builder(db_config=parse_config(path=config_file)["database"])
        self.verbose = verbose

    def __enter__(self) -> "Database":
        self.engine = create_engine(url=self.connection_string, echo=self.verbose)
        self.session = scoped_session(session_factory=sessionmaker(bind=self.engine))
        Base.metadata.create_all(bind=self.engine)
        self.logger.success("Connected to the database")
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.session.close()
        self.engine.dispose()
        self.logger.success("Disconnected from the database")

    @staticmethod
    def connection_string_builder(db_config: Dict[Any, Any]) -> str:
        """
        Create a sqlalchemy connection string using values from db_config.

        Documentation for connections strings can be found at https://docs.sqlalchemy.org/en/20/core/engines.html

        Args:
            db_config (Dict[Any, Any]): A dictionary containing database connection information.
        Returns:
            str: A sqlalchemy connection string.
        """
        if db_config["local"]:
            return f"sqlite:///{db_config['local_filepath']}"
        else:
            verify_config(config=db_config, required_keys=["host", "user", "password", "database"])
            return str(
                URL.create(
                    drivername=db_config.get("provider", "postgresql"),
                    username=db_config["user"],
                    password=db_config["password"],
                    host=db_config["host"],
                    port=db_config.get("port", 5432),
                    database=db_config["database"],
                )
            )
