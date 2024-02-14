from qe_metrics.libs.qe_metrics_base import QeMetricsBase


class Jira(QeMetricsBase):
    def __init__(self, creds_file: str) -> None:
        """
        Initialize the Jira class

        Args:
            creds_file (str): Path to the yaml file holding database and Jira credentials.
        """
        super().__init__(creds_file=creds_file)

        # TODO: Add Jira connection using config

    # TODO: Add ability to execute Jira queries
    # TODO: Validate Jira queries
