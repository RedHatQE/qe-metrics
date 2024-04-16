from typing import Any, Dict

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from pyaml_env import parse_config
from simple_logger.logger import get_logger
from urllib.parse import quote_plus

from qe_metrics.utils.general import verify_config
from qe_metrics.libs.database_mapping import Base


class Database:
    def __init__(self, config_file: str, verbose: bool) -> None:
        self.logger = get_logger(name=__name__)
        self.connection_string = self.connection_string_builder(db_config=parse_config(path=config_file)["database"])
        self.verbose = verbose
        self.engine = create_engine(url=self.connection_string, echo=self.verbose)
        Base.metadata.create_all(bind=self.engine)

    def session(self) -> Session:
        return Session(bind=self.engine)

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
            return f"sqlite:///{db_config.get('local_filepath', '/tmp/qe_metrics.sqlite')}"
        else:
            verify_config(config=db_config, required_keys=["host", "user", "password", "database"])
            driver_name = db_config.get("provider", "postgresql")
            username = db_config["user"]
            password = quote_plus(string=db_config["password"])
            host = db_config["host"]
            port = db_config.get("port", 5432)
            database = db_config["database"]
            return f"{driver_name}://{username}:{password}@{host}:{port}/{database}"
