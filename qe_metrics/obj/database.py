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
from datetime import date
from datetime import datetime

from pony import orm as pny
from simple_logger.logger import get_logger

connection = pny.Database()


class Database:
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        db_name: str,
        debug_mode: bool,
        port: int = 30327,
        provider: str = "postgres",
        init_db: bool = False,
        local_mode: bool = False,
    ) -> None:
        """
        Build the database connection and initialize the database if requested.
        Args:
            host(str): The hostname of the database server
            username(str): The username to use when connecting to the database
            password(str): The password to use when connecting to the database
            db_name(str): The name of the database to connect to
            debug_mode(bool): Whether to enable debug mode
            port(int): The port to use when connecting to the database
            provider(str): The database provider to use, defaults to postgres
            init_db(bool): Whether to initialize the database
            local_mode(bool): Whether to use a local SQLite database instead of a real database
        Returns:
            None
        """
        # Create the logger
        self.logger = get_logger(__name__)

        # Set the debug mode if specified
        if debug_mode:
            self.logger.info(
                "Debug mode enabled, database interactions will be logged",
            )
            pny.set_sql_debug(True)

        # Create the connection to the database
        self.connection = connection
        try:
            if local_mode:
                # If set, use a local SQLite database instead of a real database
                self.logger.info("Local mode enabled, using SQLite database")
                self.connection.bind(
                    provider="sqlite",
                    filename="database.sqlite",
                    create_db=True,
                )
            else:
                # Otherwise, use the actual database
                self.logger.info(
                    "Local mode disabled, using actual database connection",
                )
                self.connection.bind(
                    provider=provider,
                    host=host,
                    user=username,
                    password=password,
                    database=db_name,
                    port=port,
                )
        except Exception as error:
            self.logger.error(f"Failed to bind database connection: {error}")
            raise

        if init_db:
            # Initialize the database, if requested.
            self.logger.info("Initializing database")
            self.connection.generate_mapping(create_tables=True)
        else:
            self.connection.generate_mapping()


class JiraIssue(connection.Entity):  # type: ignore
    """
    Defines the JiraIssue table in the database.
    """

    id = pny.PrimaryKey(int, auto=True)
    date_added = pny.Required(datetime, default=datetime.now)
    issue_key = pny.Required(str)
    project = pny.Required(str)
    classification = pny.Required(str)
    link = pny.Required(str)
    date_created = pny.Required(date)
    last_updated = pny.Required(date)
    status = pny.Required(str)
    priority = pny.Required(str)
