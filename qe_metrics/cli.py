import os
from typing import Dict, Any

import click

from simple_logger.logger import get_logger

from qe_metrics.libs.config import Config


@click.group()
@click.option(
    "--config",
    "-c",
    default=os.environ.get("QE_METRICS_CONFIG", "config.yaml"),
    help="Defines the path to the config file.",
    type=click.Path(exists=True),
)
@click.option(
    "--local-db",
    is_flag=True,
    help="Use a local SQLite database instead of a real database.",
    type=click.BOOL,
)
@click.option(
    "--pdb",
    help="Drop to `ipdb` shell on exception",
    is_flag=True,
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose output of database connection.",
    type=click.BOOL,
)
def main(**kwargs: Dict[str, Any]) -> None:
    """Gather QE Metrics"""

    # Remove the pdb option from the kwargs
    kwargs.pop("pdb", None)

    # Adding noqa: F841 to ignore the unused variable until next PR, otherwise pre-commit will fail
    config = Config(config_file=str(kwargs["config"]))  # noqa: F841

    # TODO: After getting database and Jira connection in config, use them to execute the queries here
    # TODO: Populate the database with the results of the queries
    # TODO: Run a cleanup of the database to remove old entries


if __name__ == "__main__":
    should_raise = False
    _logger = get_logger(name="main-qe-metrics")
    try:
        main()
    except Exception as ex:
        import sys
        import traceback

        ipdb = __import__("ipdb")  # Bypass debug-statements pre-commit hook

        if "--pdb" in sys.argv:
            extype, value, tb = sys.exc_info()
            traceback.print_exc()
            ipdb.post_mortem(tb)
        else:
            _logger.error(ex)
            should_raise = True
    finally:
        if should_raise:
            sys.exit(1)
