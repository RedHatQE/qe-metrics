import os
import sys
from typing import Dict, Any

import click
from click import Context

from simple_logger.logger import get_logger
from pyaml_env import parse_config

from qe_metrics.libs.database import Database
from qe_metrics.libs.jira import Jira


@click.command()
@click.option(
    "--services-file",
    default=os.environ.get("QE_METRICS_SERVICES", "services.yaml"),
    help="Defines the path to the file holding a list of services and their Jira queries.",
    type=click.Path(exists=True),
)
@click.option(
    "--creds-file",
    default=os.environ.get("QE_METRICS_CREDS", "creds.yaml"),
    help="Defines the path to the file holding database and Jira credentials.",
    type=click.Path(exists=True),
)
@click.option(
    "--pdb",
    help="Drop to `ipdb` shell on exception",
    is_flag=True,
)
@click.option(
    "--verbose-db",
    is_flag=True,
    help="Verbose output of database connection.",
    type=click.BOOL,
)
@click.pass_context
def main(ctx: Context, services_file: str, creds_file: str, pdb: bool, verbose_db: bool) -> None:
    """Gather QE Metrics"""
    # Add pdb value to context
    ctx.ensure_object(dict)
    ctx.obj["PDB"] = pdb

    # Adding noqa: F841 to ignore the unused variable until next PR, otherwise pre-commit will fail
    database = Database(creds_file=creds_file)  # noqa: F841
    jira = Jira(creds_file=creds_file)  # noqa: F841

    # TODO: For each service, execute their defined Jira queries and populate the database accordingly
    # TODO: Run a cleanup of the database to remove old entries


if __name__ == "__main__":
    should_raise = False
    ctx = main.make_context("cli", sys.argv[1:]) or None
    _logger = get_logger(name="main-qe-metrics")
    try:
        main.invoke(ctx)  # type: ignore
    except Exception as ex:
        import traceback

        ipdb = __import__("ipdb")  # Bypass debug-statements pre-commit hook

        if ctx and ctx.obj is not None and ctx.obj["PDB"]:
            extype, value, tb = sys.exc_info()
            traceback.print_exc()
            ipdb.post_mortem(tb)
        else:
            _logger.error(ex)
            should_raise = True
    finally:
        if should_raise:
            sys.exit(1)
