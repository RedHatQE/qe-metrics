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
"""Module building the init-db cli command"""
from pathlib import Path

import click

from cli.commands.common_options import config_option
from cli.commands.common_options import local_option
from cli.commands.common_options import verbose_option
from cli.obj.config import Config


@verbose_option
@local_option
@config_option
@click.command("init-db")
def init_db(verbose: bool, local: bool, config: str) -> None:
    """
    Used to initialize the database.
    """
    Config(
        filepath=Path(config) if config else None,
        local=local,
        verbose=verbose,
        init_db=True,
        check_team=False,
    )
