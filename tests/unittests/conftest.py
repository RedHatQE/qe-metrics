import tempfile
import pytest
import os
import yaml
from qe_metrics.libs.database import Database


TEMP_DB_FILE = "/tmp/qe_metrics_test.sqlite"


@pytest.fixture(scope="module")
def temp_sqlite_db(temp_db_creds) -> Database:
    """
    Setup and teardown a temporary SQLite database for testing.

    Yields:
        Database: Database object
    """

    with Database(creds_file=temp_db_creds, verbose=False) as database:
        yield database

    if os.path.exists(TEMP_DB_FILE):
        os.remove(TEMP_DB_FILE)


@pytest.fixture(scope="session")
def temp_db_creds() -> str:
    """
    Setup and teardown a temporary database credentials file for testing.

    Yields:
        str: Temporary database credentials file path
    """
    creds = {
        "database": {
            "local": True,
            "local_filepath": TEMP_DB_FILE,
        }
    }

    with tempfile.NamedTemporaryFile("w", suffix=".yaml") as temp_creds:
        yaml.dump(creds, temp_creds)
        yield temp_creds.name
