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
import os
from collections.abc import Callable
from typing import Any

import click


def verbose_option(function: Callable[..., Any]) -> Callable[..., Any]:
    function = click.option(
        "--verbose",
        "-v",
        is_flag=True,
        default=False,
        help="Verbose output of database connection.",
        type=click.BOOL,
    )(function)
    return function


def local_option(function: Callable[..., Any]) -> Callable[..., Any]:
    function = click.option(
        "--local",
        "-l",
        is_flag=True,
        default=False,
        help="Use a local SQLite database instead of a real database.",
        type=click.BOOL,
    )(function)
    return function


def config_option(function: Callable[..., Any]) -> Callable[..., Any]:
    function = click.option(
        "--config",
        "-c",
        default=os.environ.get("QE_METRICS_CONFIG", ""),
        help="Defines the path to the config file.",
        type=click.Path(exists=True),
    )(function)
    return function
