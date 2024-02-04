from pathlib import Path

import click
from click import Context

from qe_metrics.utils.common_options import config_option
from qe_metrics.utils.common_options import local_option
from qe_metrics.utils.common_options import verbose_option
from qe_metrics.utils.common_options import pdb_option
from qe_metrics.libs.config import Config


@verbose_option
@local_option
@config_option
@pdb_option
@click.command("init-db")
@click.pass_context
def init_db(ctx: Context, verbose: bool, local: bool, config: str, pdb: bool) -> None:
    """
    Used to initialize the database.
    """
    ctx.obj["PDB"] = pdb
    Config(
        filepath=Path(config) if config else None,
        local=local,
        verbose=verbose,
        init_db=True,
    )
