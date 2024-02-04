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

def pdb_option(function: Callable[..., Any]) -> Callable[..., Any]:
    function = click.option(
        "--pdb",
        help="Drop to `ipdb` shell on exception",
        is_flag=True,
    )(function)
    return function
