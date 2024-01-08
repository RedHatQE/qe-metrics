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
"""Module building the init-team cli command"""
from pathlib import Path

import click

from cli.commands.common_options import config_option
from cli.commands.common_options import local_option
from cli.commands.common_options import verbose_option
from cli.commands.new_team.new_team import NewTeam
from cli.obj.config import Config


@verbose_option
@local_option
@config_option
@click.option(
    "--name",
    "-n",
    required=True,
    help="Name of team",
    type=click.STRING,
)
@click.option(
    "--email",
    "-e",
    required=True,
    help="Email for the team",
    type=click.STRING,
)
@click.command("new-team")
def new_team(name: str, email: str, verbose: bool, local: bool, config: str) -> None:
    """
    Used to insert a new team in to the database
    """
    config_obj = Config(  # type: ignore
        filepath=Path(config) if config else None,
        local=local,
        verbose=verbose,
        check_team=False,
    )

    NewTeam(name=name, email=email, config=config_obj).insert_team()
