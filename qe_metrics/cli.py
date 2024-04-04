import os
import sys

import click
from pony import orm

from simple_logger.logger import get_logger
from qe_metrics.libs.database import Database
from qe_metrics.libs.jira import Jira
from qe_metrics.utils.issue_utils import create_update_issues
from qe_metrics.utils.product_utils import products_from_file

LOGGER = get_logger(name="main-qe-metrics")


@click.command()
@click.option(
    "--products-file",
    default=os.environ.get("QE_METRICS_PRODUCTS", "products.yaml"),
    help="Defines the path to the file holding a list of products and their Jira queries.",
    type=click.Path(exists=True),
)
@click.option(
    "--config-file",
    default=os.environ.get("QE_METRICS_CONFIG", "config.yaml"),
    help="Defines the path to the file holding database and Jira configuration.",
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
def main(products_file: str, config_file: str, pdb: bool, verbose_db: bool) -> None:
    """Gather QE Metrics"""

    with Database(config_file=config_file, verbose=verbose_db), Jira(config_file=config_file) as jira, orm.db_session:
        # TODO: Run a cleanup of the database to remove old entries

        for product_dict in products_from_file(products_file=products_file):
            product, queries = product_dict.values()
            for severity, query in queries.items():
                LOGGER.info(f'Executing Jira query for "{product.name}" with severity "{severity}"')
                try:
                    create_update_issues(
                        issues=jira.search(query=query),
                        product=product,
                        severity=severity,
                        jira_server=jira.jira_config["server"],
                    )
                except Exception as ex:
                    LOGGER.error(f'Failed to update issues for "{product.name}" with severity "{severity}": {ex}')


if __name__ == "__main__":
    should_raise = False
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
            LOGGER.error(ex)
            should_raise = True

    finally:
        if should_raise:
            sys.exit(1)
