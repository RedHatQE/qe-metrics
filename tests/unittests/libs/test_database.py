from pony import orm as pny
from qe_metrics.libs.database import JiraIssues, Services
from tests.unittests.utils import sqlite_table_exists, TEMP_DB_FILE


def test_database_initialization(setup_teardown_sqlite_db):
    assert sqlite_table_exists(db_file=TEMP_DB_FILE, table_name="Services")
    assert sqlite_table_exists(db_file=TEMP_DB_FILE, table_name="JiraIssues")


@pny.db_session
def test_database_services_entry(setup_teardown_sqlite_db):
    service = Services(name="test-service-entry-service")
    all_services = Services.select()
    assert service.name in [s.name for s in all_services]


@pny.db_session
def test_database_jira_issues_entry(setup_teardown_sqlite_db):
    service = Services(name="test-jira-entry-service")
    jira_issue = JiraIssues(
        service=service,
        issue_key="TEST-1234",
        title="Test Issue",
        url="https://jira.com",
        project="TEST",
        severity="blocker",
        status="Open",
        customer_escaped=False,
        date_created="2024-01-01",
        last_updated="2024-01-01",
    )
    all_jira_issues = JiraIssues.select()
    assert jira_issue.issue_key in [j.issue_key for j in all_jira_issues]
