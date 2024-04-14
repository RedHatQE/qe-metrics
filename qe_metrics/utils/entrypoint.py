from typing import Dict, List

from pony import orm

from pyaml_env import parse_config
from simple_logger.logger import get_logger
from qe_metrics.libs.database import Database
from qe_metrics.libs.jira import Jira
from qe_metrics.utils.issue_utils import create_update_issues, delete_old_issues
from qe_metrics.utils.product_utils import append_last_updated_arg, products_from_file
from pyhelper_utils.notifications import send_slack_message


LOGGER = get_logger(name="main-qe-metrics")


def qe_metrics(products_file: str, config_file: str, verbose_db: bool) -> None:
    """Gather QE Metrics"""
    errors_for_slack: List[str] = []
    config = parse_config(path=config_file)
    data_retention_days: int = config["database"].get("data_retention_days", 90)
    slack_config: Dict[str, str] = config.get("slack", {})
    slack_webhook_url: str = slack_config.get("webhook_url", "")
    slack_webhook_error_url: str = slack_config.get("webhook_error_url", "")

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
                    err_msg = f'Failed to update issues for "{product.name}" with severity "{severity}": {ex}'
                    LOGGER.error(err_msg)
                    errors_for_slack.append(err_msg)

        if not delete_old_issues(days_old=data_retention_days):
            errors_for_slack.append("Failed to delete old issues")

        if errors_for_slack and slack_webhook_error_url:
            send_slack_message(
                webhook_url=slack_webhook_error_url,
                message="\n".join(errors_for_slack),
                raise_on_error=False,
                logger=LOGGER,
            )
        elif slack_webhook_url:
            send_slack_message(
                webhook_url=slack_webhook_url,
                message="Successfully executeed qe-metrics",
                raise_on_error=False,
                logger=LOGGER,
            )
