#
# Copyright (C) 2024 Red Hat, Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import json
import os
from pathlib import Path
from typing import Any

from simple_logger.logger import get_logger

from qe_metrics.obj.database import Database


class Config:
    def __init__(
        self,
        filepath: Path | None = None,
        local: bool = False,
        verbose: bool = False,
        init_db: bool = False,
        check_team: bool = True,
    ) -> None:
        """
        Builds the Config object
        Args:
            filepath (Path, optional): Path to the configuration file. Defaults to None.
            local (bool, optional): Whether to run in local mode. Defaults to False.
            verbose (bool, optional): Whether to run in verbose mode. Defaults to False.
            init_db (bool, optional): Whether to initialize the database. Defaults to False.
            check_team (bool, optional): Whether to check that the team exists in the database. Defaults to True.
        Returns:
            None
        """
        self.logger = get_logger(__name__)

        # Define the filepath and load the configuration file
        self.filepath = filepath or self._get_filepath()
        self.config_dict = self._load_config(filepath=self.filepath)

        # Establish a connection to the database
        self.database = self._get_database(
            config_dict=self.config_dict,
            local=local,
            verbose=verbose,
            init_db=init_db,
        )

    def _load_config(self, filepath: Path) -> dict[Any, Any]:
        """
        Loads the configuration file
        Args:
            filepath (Path, optional): Path to the configuration file. Defaults to None.
        Returns:
            dict: Configuration file as a dictionary
        """
        self.logger.info(f"Loading configuration file at {filepath}")

        # Read the contents of the config file
        try:
            with open(str(filepath)) as file:
                config_data = file.read()
        except Exception:
            self.logger.error(
                f"Unable to read configuration file at {filepath}. Please verify permissions/path and try again.",
            )
            exit(1)

        # Verify that the config data is properly formatted JSON
        try:
            config_dict = json.loads(config_data)
        except json.decoder.JSONDecodeError as error:
            self.logger.error(
                "Config contains malformed JSON:",
            )
            self.logger.error(error)
            exit(1)

        return config_dict

    def _get_filepath(self) -> Path:
        """
        Returns the filepath to the configuration file
        Returns:
            Path: Path to the configuration file
        """
        filepath = Path(
            os.getenv("QE_METRICS_CONFIG")  # type: ignore
            if os.getenv("QE_METRICS_CONFIG")
            else "./qe-metrics.config",
        )
        if not filepath.exists():
            self.logger.error(
                "No configuration file specified or config not found. Please specify a configuration file using the "
                "--config option or setting the $QE_METRICS_CONFIG environment variable.",
            )
            exit(1)
        return filepath

    def _get_database(
        self,
        config_dict: dict[Any, Any],
        local: bool,
        verbose: bool,
        init_db: bool,
    ) -> Database:
        """
        Returns a Database object
        Args:
            config_dict (dict): Configuration file as a dictionary
            local (bool): Whether to run in local mode
            verbose (bool): Whether to run in verbose mode
            init_db (bool): Whether to initialize the database
        Returns:
            Database: Database object
        """
        host = config_dict.get("database_auth", {}).get("host")
        username = config_dict.get("database_auth", {}).get("username")
        password = config_dict.get("database_auth", {}).get("password")
        db_name = config_dict.get("database_auth", {}).get("database")
        port = config_dict.get("database_auth", {}).get("port", 30327)
        provider = config_dict.get("database_auth", {}).get("provider", "postgres")

        # Verify that the database connection information is present in the config file
        if not host or not username or not password or not db_name:
            self.logger.error(
                'Database connection information not complete in config. Please validate the "database_auth" '
                'section of the config file.',
            )
            exit(1)

        return Database(
            host=host,
            username=username,
            password=password,
            db_name=db_name,
            port=port,
            provider=provider,
            debug_mode=verbose,
            init_db=init_db,
            local_mode=local,
        )
