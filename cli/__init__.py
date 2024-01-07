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
"""Module building qe-metrics cli"""
import click

from cli.commands.clean_db import clean_db
from cli.commands.gather_jira import gather_jira
from cli.commands.init_config import init_config
from cli.commands.init_db import init_db
from cli.commands.new_team import new_team


@click.group()
@click.pass_context
def cli(ctx: click.Option) -> None:
    pass


cli.add_command(new_team)  # type: ignore
cli.add_command(init_db)  # type: ignore
cli.add_command(init_config)  # type: ignore
cli.add_command(gather_jira)  # type: ignore
cli.add_command(clean_db)  # type: ignore
