from qe_metrics.libs.qe_metrics_base import QeMetricsBase


class Database(QeMetricsBase):
    def __init__(self, creds_file: str) -> None:
        """
        Initialize the Database class
        Args:
            creds_file (str): Path to the yaml file holding database and Jira credentials.

        """
        super().__init__(creds_file=creds_file)

        # TODO: Add database connection


# TODO: Define database schema here
