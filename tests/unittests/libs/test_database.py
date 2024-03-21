import pytest


@pytest.mark.parametrize(
    "product",
    [("test-product-entry-product", {"blocker": "BLOCKER QUERY", "critical-blocker": "CRITICAL BLOCKER QUERY"})],
    indirect=True,
)
def test_database_products_entry(tmp_sqlite_db, product, db_session):
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
def test_database_jira_issues_entry(tmp_sqlite_db, product, jira_issue, db_session):
    all_jira_issues = tmp_sqlite_db.JiraIssues.select()
    assert jira_issue.issue_key in [
        issue.issue_key for issue in all_jira_issues
    ], f"Test Jira issue {jira_issue.issue_key} not found in database."


@pytest.mark.parametrize(
    "tmp_products_file",
    [{"test-from-file-product": {"blocker": "BLOCKER QUERY", "critical-blocker": "CRITICAL BLOCKER QUERY"}}],
    indirect=True,
)
def test_database_products_from_file(tmp_sqlite_db, tmp_products_file, db_session):
    tmp_sqlite_db.Products.from_file(products_file=tmp_products_file)
    all_products = tmp_sqlite_db.Products.select()
    assert "test-from-file-product" in [
        product.name for product in all_products
    ], "Test product test-from-file-product not found in database."
