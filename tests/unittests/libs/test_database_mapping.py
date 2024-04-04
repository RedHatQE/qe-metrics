import pytest
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
                    "customer_escaped": False,
                    "date_created": "2024-01-01",
                    "last_updated": "2024-01-01",
                }
            ],
        )
    ],
    indirect=True,
)
def test_database_jira_issues_entry(product, jira_issues):
    all_jira_issues = JiraIssuesEntity.select()
    assert jira_issues[0].issue_key in [
        _issue.issue_key for _issue in all_jira_issues
    ], f"Test Jira issue {jira_issues[0].issue_key} not found in database."


@pytest.mark.parametrize(
    "product",
    [("test-product-entry-product")],
    indirect=True,
)
def test_database_products_entry(product):
    all_products = ProductsEntity.select()
    assert product.name in [
        _product.name for _product in all_products
    ], f"Test product {product.name} not found in database."
