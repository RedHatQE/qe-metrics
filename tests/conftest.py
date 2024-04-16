from datetime import datetime, timezone
import pytest
import yaml
from sqlalchemy.orm import Session
from qe_metrics.libs.database import Database
from qe_metrics.libs.database_mapping import ProductsEntity, JiraIssuesEntity


@pytest.fixture
def db_session(tmp_db_config) -> Session:
    db = Database(config_file=tmp_db_config, verbose=False)
    with db.session() as db_session:
        yield db_session


@pytest.fixture
def tmp_db_config(tmp_path_factory) -> str:
    tmp_dir = tmp_path_factory.mktemp(basename="qe-metrics-test")

    config = {
        "database": {
            "local": True,
            "local_filepath": ":memory:",
        }
    }

    with open(tmp_dir / "config.yaml", "w") as tmp_config:
        yaml.dump(config, tmp_config)
    yield tmp_config.name


@pytest.fixture
def tmp_products_file(tmp_path, request):
    products = request.param
    products_file = tmp_path / "products.yaml"
    with open(products_file, "w") as tmp_products:
        yaml.dump(products, tmp_products)
    yield products_file


@pytest.fixture
def product(request, db_session):
    product = ProductsEntity(name=request.param)
    db_session.add(instance=product)
    return product


@pytest.fixture
def jira_issues(request, db_session, product):
    jira_issues = []
    for issue in request.param:
        jira_issue = JiraIssuesEntity(product=product, **issue)
        jira_issues.append(jira_issue)
    db_session.add_all(instances=jira_issues)
    yield jira_issues


@pytest.fixture
def raw_jira_issues(request, mocker):
    issues = []
    for issue in request.param:
        mock_issue = mocker.MagicMock()
        mock_issue.key = issue["key"]
        mock_issue.fields.project.key = issue["key"].split("-")[0]
        mock_issue.fields.summary = issue["title"]
        mock_issue.fields.status.name = issue.get("status", "In Progress")
        mock_issue.fields.issuetype.name = issue.get("issue_type", "bug")
        mock_issue.fields.customfield_12313440 = issue.get("customer_escaped", "0.0")
        mock_issue.is_customer_escaped = float(getattr(mock_issue.fields, "customfield_12313440")) > 0
        mock_issue.fields.updated = issue.get(
            "last_updated", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        )
        mock_issue.fields.created = issue.get("created", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%z"))
        issues.append(mock_issue)
    yield issues
