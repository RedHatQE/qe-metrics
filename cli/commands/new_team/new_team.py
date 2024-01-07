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
import re

from pony import orm as pny
from simple_logger.logger import get_logger

from cli.obj.config import Config
from cli.obj.database import Team


class NewTeam:
    def __init__(self, name: str, email: str, config: Config) -> None:
        """
        Builds the NewTeam object which is used to insert a new team in to the database.
        Args:
            name (str): Name of the team
            email (str): Email for the team
            config (Config): Valid Config object
        Returns:
            None
        """
        self.logger = get_logger(__name__)
        self.name = self._get_team_name(name)
        self.email = self._get_team_email(email)
        self.database = config.database

    @pny.db_session
    def insert_team(self) -> None:
        """
        Inserts a new team in to the database.
        Returns:
            None
        """
        self.logger.info(f"Creating team {self.name} with email {self.email}.")
        try:
            new_team = Team(name=self.name, email=self.email)
            pny.commit()
            self.logger.info(f"Successfully created team with ID: {new_team.id}")
        except Exception as error:
            self.logger.error(
                f"Failed to create team {self.name} with email {self.email}.",
            )
            self.logger.error(error)
            exit(1)

    @pny.db_session
    def _get_team_name(self, name: str) -> str:
        """
        Validates the team name and verifies that it does not already exist in the database.
        Args:
            name (str): Name of the team
        Returns:
            str: Valid team name
        """
        if isinstance(name, str):
            # Check for any spaces in the name
            if " " in name:
                self.logger.error(
                    f"Team name value cannot contain spaces.",
                )
                exit(1)

            # Check if the team name already exists in the database
            existing_team = pny.select(t for t in Team if t.name == name).first()  # type: ignore
            if existing_team:
                self.logger.error(
                    f"Team already exists.",
                )
                exit(1)

            return name
        else:
            self.logger.error(
                f"Team name value not a string.",
            )
            exit(1)

    def _get_team_email(self, email: str) -> str:
        """
        Validates the team email.
        Args:
            email (str): Email for the team
        Returns:
            str: Valid email
        """
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

        if isinstance(email, str):
            # Verify that the string provided is a valid email
            if re.fullmatch(regex, email):
                return email
            else:
                self.logger.error(
                    f"Email value not a valid email.",
                )
                exit(1)
        else:
            self.logger.error(
                f"Email value not a string.",
            )
            exit(1)
