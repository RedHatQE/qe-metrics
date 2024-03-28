import pytest
import yaml

from qe_metrics.libs.database import Database
from pony import orm


@pytest.fixture(scope="module")
def db_session():
    with orm.db_session:
        yield


@pytest.fixture(scope="session")
def tmp_sqlite_db(tmp_db_config) -> Database:
    with Database(config_file=tmp_db_config, verbose=False) as database:
        yield database


@pytest.fixture(scope="session")
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
def product(db_session, tmp_sqlite_db, request):
    product_name, queries = request.param
    return tmp_sqlite_db.Products(name=product_name, queries=queries)


@pytest.fixture
def jira_issues(db_session, tmp_sqlite_db, product, request):
    jira_issues = []
    with orm.db_session:
        for issue in request.param:
            jira_issue = tmp_sqlite_db.JiraIssues(product=product, **issue)
            jira_issues.append(jira_issue)
        yield jira_issues


@pytest.fixture
def raw_jira_issues(request, mocker):
    issues = []
    for issue in request.param:
        mock_issue = mocker.MagicMock()
        mock_issue.key = issue["key"]
        mock_issue.fields.summary = issue["title"]
        mock_issue.fields.status.name = issue["status"]
        mock_issue.fields.customfield_12313440 = issue["customer_escaped"]
        mock_issue.is_customer_escaped = float(getattr(mock_issue.fields, "customfield_12313440")) > 0
        mock_issue.fields.updated = issue["last_updated"]
        issues.append(mock_issue)
    yield issues
