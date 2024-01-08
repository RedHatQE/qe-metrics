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

from pony import orm as pny
from simple_logger.logger import get_logger

from cli.obj.database import Database
from cli.obj.database import Team
from cli.obj.gather_jira_rule import GatherJiraRule
from cli.obj.jira import Jira


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

        # Establish a connection to Jira
        self.jira = self._get_jira(config_dict=self.config_dict)
        self.jira_server = self.config_dict.get("jira_auth", {}).get("server")

        # Establish a connection to the database
        self.database = self._get_database(
            config_dict=self.config_dict,
            local=local,
            verbose=verbose,
            init_db=init_db,
        )

        # Define the gather_jira rules
        self.gather_jira_data_retention = self._get_gather_jira_data_retention(
            config_dict=self.config_dict,
        )
        self.gather_jira_team = self._get_gather_jira_team(
            config_dict=self.config_dict,
            check_team=check_team,
        )
        self.gather_jira_rules = self._get_gather_jira_rules(
            config_dict=self.config_dict,
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
                "No configuration file specified or config not found. Please specify a configuration file using the --config option or setting the $QE_METRICS_CONFIG environment variable.",
            )
            exit(1)
        return filepath

    def _get_jira(self, config_dict: dict[Any, Any]) -> Jira:
        """
        Returns a Jira object
        Args:
            config_dict (dict): Configuration file as a dictionary
        Returns:
            Jira: Jira object
        """
        token = config_dict.get("jira_auth", {}).get("token")
        server = config_dict.get("jira_auth", {}).get("server")

        # Verify that the token and server are present in the config file
        if not token or not server:
            self.logger.error(
                "Jira authentication token or server not found in config file.",
            )
            exit(1)

        return Jira(
            token=token,
            server=server,
        )

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
                'Database connection information not complete in config. Please validate the "database_auth" section of the config file.',
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

    def _get_gather_jira_data_retention(self, config_dict: dict[Any, Any]) -> int:
        """
        Returns the number of days to retain Jira data
        Args:
            config_dict (dict): Configuration file as a dictionary
        Returns:
            int: Number of days to retain Jira data
        """
        data_retention = config_dict.get("gather_jira", {}).get(
            "data_retention_days",
            90,
        )

        if not isinstance(data_retention, int):
            self.logger.error(
                '"data_retention" value in "gather_jira" section of config file is not an integer.',
            )
            exit(1)

        return data_retention

    @pny.db_session
    def _get_gather_jira_team(
        self,
        config_dict: dict[Any, Any],
        check_team: bool,
    ) -> str:
        """
        Returns the name of the team to gather Jira data for
        Args:
            config_dict (dict): Configuration file as a dictionary
            check_team (bool): Whether to check that the team exists in the database
        Returns:
            str: Name of the team to gather Jira data for
        """
        team_name = config_dict.get("gather_jira", {}).get("team_name")

        # Exit if team_name is not defined
        if not team_name:
            self.logger.error(
                '"team_name" value not found in "gather_jira" section of config file.',
            )
            exit(1)
        # Exit if team_name is not a string
        if not isinstance(team_name, str):
            self.logger.error(
                '"team_name" value in "gather_jira" section of config file is not a string.',
            )
            exit(1)

        # Exit if team_name is not found in database
        if not check_team or pny.select(t for t in Team if t.name == team_name).first():  # type: ignore
            return team_name
        else:
            self.logger.error(f'Team name "{team_name}" not found in database')

            exit(1)

    def _get_gather_jira_rules(
        self,
        config_dict: dict[Any, Any],
    ) -> list[GatherJiraRule]:
        """
        Returns a list of GatherJiraRule objects
        Args:
            config_dict (dict): Configuration file as a dictionary
        Returns:
            list[GatherJiraRule]: List of GatherJiraRule objects
        """
        raw_rules_list = config_dict.get("gather_jira", {}).get("rules", [])
        return_list = []

        for rule_dict in raw_rules_list:
            return_list.append(GatherJiraRule(rule_dict=rule_dict))

        return return_list
