import pytest
from pony import orm


@pytest.mark.parametrize(
    "product",
    [("test-product-entry-product", {"blocker": "BLOCKER QUERY", "critical-blocker": "CRITICAL BLOCKER QUERY"})],
    indirect=True,
)
@orm.db_session
def test_database_products_entry(tmp_sqlite_db, product):
    all_products = tmp_sqlite_db.Products.select()
    assert product.name in [
        product.name for product in all_products
    ], f"Test product {product.name} not found in database."


@pytest.mark.parametrize(
    "product",
    [("test-jira-entry-product", {"blocker": "BLOCKER QUERY", "critical-blocker": "CRITICAL BLOCKER QUERY"})],
    indirect=True,
)
@pytest.mark.parametrize(
    "jira_issue",
    [
        {
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
    ],
    indirect=True,
)
@orm.db_session
def test_database_jira_issues_entry(tmp_sqlite_db, product, jira_issue):
    all_jira_issues = tmp_sqlite_db.JiraIssues.select()
    assert jira_issue.issue_key in [
        issue.issue_key for issue in all_jira_issues
    ], f"Test Jira issue {jira_issue.issue_key} not found in database."
