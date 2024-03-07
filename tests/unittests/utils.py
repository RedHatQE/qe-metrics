import os
import tempfile
import yaml
import sqlite3
import pytest
from qe_metrics.libs.database import Database

TEMP_DB_FILE = "/tmp/qe_metrics_test.sqlite"


def temp_db_creds():
    creds = {
        "database": {
            "local": True,
            "local_filepath": TEMP_DB_FILE,
        }
    }

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml") as temp_creds:
        yaml.dump(creds, temp_creds)
        return temp_creds.name


def sqlite_table_exists(db_file: str, table_name: str) -> bool:
    # Connect to the SQLite database
    with sqlite3.connect(db_file) as conn:
        # Create a cursor object
        cursor = conn.cursor()

        # Execute the SQL query
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        # Fetch all the rows
        tables = cursor.fetchall()

        return table_name in [table[0] for table in tables]


@pytest.fixture(scope="module", autouse=True)
def setup_teardown_sqlite_db():
    # Test setup
    temp_creds_file = temp_db_creds()
    Database(creds_file=temp_creds_file, verbose=False)

    yield

    # Test teardown
    os.remove(TEMP_DB_FILE)
    os.remove(temp_creds_file)
