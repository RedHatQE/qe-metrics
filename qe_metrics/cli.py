import click
import datetime
import time
import sys

from click import Context

from qe_metrics.commands.init_db import init_db
from simple_logger.logger import get_logger
from qe_metrics.utils.common_options import pdb_option


@click.group()
@pdb_option
@click.pass_context
def main(ctx: Context, pdb: bool) -> None:
    ctx.ensure_object(dict)
    ctx.obj["PDB"] = pdb


main.add_command(init_db)  # type: ignore


if __name__ == "__main__":
    start_time = time.time()
    should_raise = False
    _logger = get_logger(name="main-qe-metrics")
    ctx = main.make_context("cli", sys.argv[1:]) or None
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
        _logger.info(f"Total execution time: {datetime.timedelta(seconds=time.time() - start_time)}")
        if should_raise:
            sys.exit(1)
