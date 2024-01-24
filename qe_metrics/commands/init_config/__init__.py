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
"""Module building the init-config cli command"""
from pathlib import Path

import click
from jinja2 import Environment
from jinja2 import FileSystemLoader
from simple_logger.logger import get_logger


@click.argument(
    "filepath",
    type=click.Path(exists=False),
    default="./qe-metrics.config",
)
@click.command("init-config")
def init_config(filepath: str) -> None:
    """
    Creates an empty config file at the specified filepath.
    """
    logger = get_logger(__name__)

    template_path = Path("qe_metrics/templates/qe-metrics.config.j2")
    env = Environment(loader=FileSystemLoader(template_path.parent))
    template = env.get_template(template_path.name)
    rendered_template = template.render()

    with open(filepath, "w") as file:
        file.write(rendered_template)

    logger.info(f"Config file written to {filepath}")
