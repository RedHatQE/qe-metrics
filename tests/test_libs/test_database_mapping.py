import pytest
from datetime import datetime

from qe_metrics.libs.database_mapping import JiraIssuesEntity, ProductsEntity


@pytest.mark.parametrize(
    "product, jira_issues",
    [
        pytest.param(
            ("test-jira-entry-product"),
            [
                {
                    "issue_key": "TEST-1234",
                    "title": "Test Issue",
                    "url": "https://jira.com",
                    "project": "TEST",
                    "severity": "blocker",
                    "status": "Open",
                    "issue_type": "bug",
                    "customer_escaped": False,
                    "date_created": datetime.strptime("2024-01-01", "%Y-%m-%d").date(),
                    "last_updated": datetime.strptime("2024-01-01", "%Y-%m-%d").date(),
                }
            ],
        )
    ],
    indirect=True,
)
def test_database_jira_issues_entry(jira_issues, tmp_sqlite_db):
    assert jira_issues[0].issue_key in [
        _issue.issue_key for _issue in tmp_sqlite_db.session.query(JiraIssuesEntity).all()
    ], f"Test Jira issue {jira_issues[0].issue_key} not found in database."


@pytest.mark.parametrize(
    "product",
    [("test-product-entry-product")],
    indirect=True,
)
def test_database_products_entry(product, tmp_sqlite_db):
    assert product.name in [
        _product.name for _product in tmp_sqlite_db.session.query(ProductsEntity).all()
    ], f"Test product {product.name} not found in database."
