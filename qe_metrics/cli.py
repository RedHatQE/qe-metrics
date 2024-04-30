import os
import time
from multiprocessing import Process
from typing import Any, Dict

import click

from pyaml_env import parse_config
from simple_logger.logger import get_logger
from qe_metrics.utils.entrypoint import qe_metrics
from qe_metrics.utils.general import run_in_verbose
from pyhelper_utils.runners import function_runner_with_pdb
from pyhelper_utils.general import tts
from flask.logging import default_handler
from flask import Flask


APP = Flask("qe_metrics")
APP.logger.removeHandler(default_handler)
APP.logger.addHandler(get_logger(APP.logger.name).handlers[0])


def run_in_while(config_file: str, verbose_db: bool) -> None:
    while True:
        config = parse_config(path=config_file)
        run_interval = config.get("run_interval", "24h")

        try:
            qe_metrics(products_file_url=True, config_file=config_file, verbose_db=verbose_db)
        except Exception as ex:
            APP.logger.error(f"Failed to run qe_metrics: {ex}")

        APP.logger.info(f"Sleeping for {run_interval}")
        time.sleep(tts(ts=run_interval))


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


@APP.route("/update", methods=["GET"])
def update_qe_metrics() -> str:
    qe_metrics(
        products_file_url=True,
        config_file=os.environ.get("QE_METRICS_CONFIG", "config.yaml"),
        verbose_db=run_in_verbose(),
    )
    return "OK"


@APP.route("/healthcheck")
def healthcheck() -> str:
    return "alive"


if __name__ == "__main__":
    # To not run `qe_metrics` in `while loop` (for debugging) set QE_METRICS_LOCAL_DEBUG=1
    qe_metrics_kwargs: Dict[str, Any] = {
        "config_file": os.environ.get("QE_METRICS_CONFIG", "config.yaml"),
        "verbose_db": run_in_verbose(),
    }
    if os.environ.get("QE_METRICS_LOCAL_DEBUG"):
        qe_metrics_kwargs["products_file_url"] = True
        qe_metrics(**qe_metrics_kwargs)
        exit(0)

    proc = Process(
        target=run_in_while,
        kwargs=qe_metrics_kwargs,
    )
    proc.start()

    APP.logger.info(f"Starting {APP.name} app")
    APP.run(
        port=int(os.environ.get("QE_METRICS_LISTEN_PORT", 5000)),
        host=os.environ.get("QE_METRICS_LISTEN_IP", "127.0.0.1"),
        use_reloader=True if os.environ.get("QE_METRICS_USE_RELOAD") else False,
    )
