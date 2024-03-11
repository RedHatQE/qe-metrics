import pytest
from pony import orm


@pytest.fixture
def fake_jira_issue():
    return {
        "issue_key": "TEST-1234",
        "title": "Test Issue",
        "url": "https://jira.com",
        "project": "TEST",
        "severity": "blocker",
        "status": "Open",
        "customer_escaped": False,
        "date_created": "2024-01-01",
        "last_updated": "2024-01-01",
    }


@pytest.mark.usefixtures("temp_sqlite_db")
@orm.db_session
def test_database_services_entry(temp_sqlite_db):
    test_service = temp_sqlite_db.Services(name="test-service-entry-service")
    all_services = temp_sqlite_db.Services.select()
    assert test_service.name in [service.name for service in all_services], "Test service not found in database."


@pytest.mark.usefixtures("temp_sqlite_db", "fake_jira_issue")
@orm.db_session
def test_database_jira_issues_entry(temp_sqlite_db, fake_jira_issue):
    service = temp_sqlite_db.Services(name="test-jira-entry-service")
    test_jira_issue = temp_sqlite_db.JiraIssues(service=service, **fake_jira_issue)
    all_jira_issues = temp_sqlite_db.JiraIssues.select()
    assert test_jira_issue.issue_key in [
        issue.issue_key for issue in all_jira_issues
    ], "Test Jira issue not found in database."
