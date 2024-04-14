import os

import click
from pony import orm

from pyaml_env import parse_config
from simple_logger.logger import get_logger
from qe_metrics.libs.database import Database
from qe_metrics.libs.jira import Jira
from qe_metrics.utils.issue_utils import create_update_issues, delete_old_issues
from qe_metrics.utils.product_utils import append_last_updated_arg, products_from_file
from pyhelper_utils.runners import function_runner_with_pdb

LOGGER = get_logger(name="main-qe-metrics")


def qe_metrics(products_file: str, config_file: str, verbose_db: bool) -> None:
    """Gather QE Metrics"""
    data_retention_days = parse_config(path=config_file)["database"].get("data_retention_days", 90)

    with Database(config_file=config_file, verbose=verbose_db), Jira(config_file=config_file) as jira, orm.db_session:
        for product_dict in products_from_file(products_file=products_file):
            product, queries = product_dict.values()
            for severity, query in queries.items():
                LOGGER.info(f'Executing Jira query for "{product.name}" with severity "{severity}"')
                try:
                    if query := append_last_updated_arg(query=query, look_back_days=data_retention_days):
                        create_update_issues(
                            issues=jira.search(query=query),
                            product=product,
                            severity=severity,
                            jira_server=jira.jira_config["server"],
                        )
                except Exception as ex:
                    LOGGER.error(f'Failed to update issues for "{product.name}" with severity "{severity}": {ex}')
        delete_old_issues(days_old=data_retention_days)


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
def cli_entrypoint(products_file: str, config_file: str, pdb: bool, verbose_db: bool) -> None:
    function_runner_with_pdb(
        func=qe_metrics,
        products_file=products_file,
        config_file=config_file,
        verbose_db=verbose_db,
    )


if __name__ == "__main__":
    cli_entrypoint()
