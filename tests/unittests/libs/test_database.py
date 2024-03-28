import datetime
import pytest

from qe_metrics.libs.database import Database


@pytest.mark.parametrize(
    "product",
    [("test-product-entry-product", {"blocker": "BLOCKER QUERY", "critical-blocker": "CRITICAL BLOCKER QUERY"})],
    indirect=True,
)
def test_database_products_entry(tmp_sqlite_db, product):
    all_products = tmp_sqlite_db.Products.select()
    assert product.name in [
        _product.name for _product in all_products
    ], f"Test product {product.name} not found in database."


@pytest.mark.parametrize(
    "product, jira_issues",
    [
        pytest.param(
            ("test-jira-entry-product", {"blocker": "BLOCKER QUERY", "critical-blocker": "CRITICAL BLOCKER QUERY"}),
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
        )
    ],
    indirect=True,
)
def test_database_jira_issues_entry(tmp_sqlite_db, product, jira_issues):
    all_jira_issues = tmp_sqlite_db.JiraIssues.select()
    assert jira_issues[0].issue_key in [
        _issue.issue_key for _issue in all_jira_issues
    ], f"Test Jira issue {jira_issues[0].issue_key} not found in database."


@pytest.mark.parametrize(
    "tmp_products_file",
    [{"test-from-file-product": {"blocker": "BLOCKER QUERY", "critical-blocker": "CRITICAL BLOCKER QUERY"}}],
    indirect=True,
)
def test_database_products_from_file(tmp_sqlite_db, tmp_products_file, db_session):
    tmp_sqlite_db.Products.from_file(products_file=tmp_products_file)
    all_products = tmp_sqlite_db.Products.select()
    assert "test-from-file-product" in [
        _product.name for _product in all_products
    ], "Test product test-from-file-product not found in database."


@pytest.mark.parametrize(
    "product, raw_jira_issues, jira_issues",
    [
        pytest.param(
            (
                "update-existing-issue-product",
                {"blocker": "BLOCKER QUERY", "critical-blocker": "CRITICAL BLOCKER QUERY"},
            ),
            [
                {
                    "key": "TEST-1234",
                    "title": "New Test Summary",
                    "status": "In Progress",
                    "customer_escaped": "0.0",
                    "last_updated": "2023-12-31T23:59:59.999999+0000",
                }
            ],
            [
                {
                    "issue_key": "TEST-1234",
                    "title": "Test Summary",
                    "url": "https://jira.com",
                    "project": "TEST",
                    "severity": "blocker",
                    "status": "To Do",
                    "customer_escaped": True,
                    "date_created": "2024-12-29",
                    "last_updated": "2024-12-30",
                }
            ],
        ),
    ],
    indirect=True,
)
def test_update_existing_issue(product, raw_jira_issues, jira_issues):
    jira_issues[0].update_existing_issue(new_issue_data=raw_jira_issues[0], severity="critical")
    expected_values = {
        "title": "New Test Summary",
        "severity": "critical",
        "status": "In Progress",
        "customer_escaped": False,
        "last_updated": datetime.date(2023, 12, 31),
    }
    actual_values = {
        "title": jira_issues[0].title,
        "severity": jira_issues[0].severity,
        "status": jira_issues[0].status,
        "customer_escaped": jira_issues[0].customer_escaped,
        "last_updated": jira_issues[0].last_updated,
    }
    assert actual_values == expected_values, f"{actual_values} != {expected_values}"


@pytest.mark.parametrize(
    "product, raw_jira_issues, jira_issues",
    [
        pytest.param(
            (
                "mark-stale-issues-product",
                {"blocker": "BLOCKER QUERY", "critical-blocker": "CRITICAL BLOCKER QUERY"},
            ),
            [
                {
                    "key": "TEST-1234",
                    "title": "Test Summary",
                    "status": "In Progress",
                    "customer_escaped": "0.0",
                    "last_updated": "2023-12-31T23:59:59.999999+0000",
                },
                {
                    "key": "TEST-1236",
                    "title": "Test Summary",
                    "status": "In Progress",
                    "customer_escaped": "0.0",
                    "last_updated": "2023-12-31T23:59:59.999999+0000",
                },
            ],
            [
                {
                    "issue_key": "TEST-1234",
                    "title": "Test Summary",
                    "url": "https://jira.com",
                    "project": "TEST",
                    "severity": "blocker",
                    "status": "In Progress",
                    "customer_escaped": False,
                    "date_created": "2024-12-30",
                    "last_updated": "2024-12-31",
                },
                {
                    "issue_key": "TEST-1235",
                    "title": "Test Summary",
                    "url": "https://jira.com",
                    "project": "TEST",
                    "severity": "blocker",
                    "status": "In Progress",
                    "customer_escaped": False,
                    "date_created": "2024-12-30",
                    "last_updated": "2024-12-31",
                },
            ],
        ),
    ],
    indirect=True,
)
def test_mark_stale_issues(tmp_sqlite_db, product, raw_jira_issues, jira_issues):
    Database.JiraIssues.mark_stale_issues(current_issues=raw_jira_issues, db_issues=jira_issues, product=product)
    assert tmp_sqlite_db.JiraIssues.get(lambda issue: issue.issue_key == "TEST-1235").status == "stale"
