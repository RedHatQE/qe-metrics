import datetime
import pytest
from qe_metrics.libs.orm_database import JiraIssuesEntity, ProductsEntity
from qe_metrics.libs.database import update_existing_issue, mark_stale_issues, products_from_file, create_update_issues

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
def test_database_update_existing_issue(product, raw_jira_issues, jira_issues):
    update_existing_issue(existing_issue=jira_issues[0], new_issue_data=raw_jira_issues[0], severity="critical")
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
                    "key": "TEST-1134",
                    "title": "Test Summary",
                },
                {
                    "key": "TEST-1136",
                    "title": "Test Summary",
                },
            ],
            [
                {
                    "issue_key": "TEST-1134",
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
                    "issue_key": "TEST-1135",
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
def test_database_mark_stale_issues(product, raw_jira_issues, jira_issues):
    mark_stale_issues(current_issues=raw_jira_issues, db_issues=jira_issues, product=product)
    assert JiraIssuesEntity.get(lambda issue: issue.issue_key == "TEST-1135").status == "stale"

@pytest.mark.parametrize(
    "tmp_products_file",
    [{"test-from-file-product": {"blocker": "BLOCKER QUERY", "critical-blocker": "CRITICAL BLOCKER QUERY"}}],
    indirect=True,
)
def test_database_products_from_file(tmp_products_file):
    products_from_file(products_file=tmp_products_file)
    all_products = ProductsEntity.select()
    assert "test-from-file-product" in [
        _product.name for _product in all_products
    ], "Test product test-from-file-product not found in database."

@pytest.mark.parametrize(
    "product, raw_jira_issues",
    [
        pytest.param(
            (
                "create-update-issues-product",
                {"blocker": "BLOCKER QUERY", "critical-blocker": "CRITICAL BLOCKER QUERY"},
            ),
            [
                {
                    "key": "NEW-1234",
                    "title": "Test Summary",
                    "customer_escaped": "1.0",
                },
            ],
            
        ),
    ],
    indirect=True,
)
def test_database_create_update_issues_creates_issues(product, raw_jira_issues):
    create_update_issues(issues=raw_jira_issues, product=product, severity="blocker", jira_server="https://jira.com")
    assert JiraIssuesEntity.get(issue_key="NEW-1234", product=product)


@pytest.mark.parametrize(
    "product, raw_jira_issues",
    [
        pytest.param(
            (
                "create-update-issues-none_bugs_not_created_product",
                {"blocker": "BLOCKER QUERY", "critical-blocker": "CRITICAL BLOCKER QUERY"},
            ),
            [
                {
                    "key": "TASK-1234",
                    "title": "Test Summary",
                    "issue_type": "Task",
                },
            ],
            
        ),
    ],
    indirect=True,
)
def test_database_create_update_issues_none_bugs_not_created(product, raw_jira_issues):
    create_update_issues(issues=raw_jira_issues, product=product, severity="blocker", jira_server="https://jira.com")
    assert not JiraIssuesEntity.get(issue_key="TASK-1234", product=product)