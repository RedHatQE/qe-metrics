import pytest
from qe_metrics.utils.general import verify_config, verify_queries, format_issue_date
from datetime import date


@pytest.fixture
def valid_config():
    return {"key1": "value1", "key2": "value2"}


@pytest.fixture
def config_none_value():
    return {"key1": "value1", "key2": None}


@pytest.fixture
def valid_queries():
    return {"blocker": "query1", "critical-blocker": "query2"}


@pytest.fixture
def queries_missing_value():
    return {"blocker": "query"}


@pytest.fixture
def queries_none_value():
    return {"blocker": "query1", "critical-blocker": None}


@pytest.fixture
def queries_extra():
    return {"blocker": "query1", "critical-blocker": "query2", "extra": "query3"}


def test_verify_config_with_all_required_keys_present(valid_config):
    required_keys = ["key1", "key2"]
    verify_config(config=valid_config, required_keys=required_keys)


def test_verify_config_with_missing_keys_raises_value_error(valid_config):
    required_keys = ["key1", "key2", "key3"]
    with pytest.raises(ValueError):
        verify_config(config=valid_config, required_keys=required_keys)


def test_verify_config_with_none_values_raises_value_error(config_none_value):
    required_keys = ["key1", "key2"]
    with pytest.raises(ValueError):
        verify_config(config=config_none_value, required_keys=required_keys)


def test_verify_queries_with_all_required_queries_present(valid_queries):
    verify_queries(queries_dict=valid_queries)


def test_verify_queries_with_missing_queries_raises_value_error(queries_missing_value):
    with pytest.raises(ValueError):
        verify_queries(queries_dict=queries_missing_value)


def test_verify_queries_with_none_values_raises_value_error(queries_none_value):
    with pytest.raises(ValueError):
        verify_queries(queries_dict=queries_none_value)


def test_verify_queries_with_extra_queries_raises_value_error(queries_extra):
    with pytest.raises(ValueError):
        verify_queries(queries_dict=queries_extra)


@pytest.mark.parametrize(
    "raw_jira_issues",
    [
        [
            {
                "key": "TEST-1234",
                "title": "New Test Summary",
                "status": "In Progress",
                "customer_escaped": "0.0",
                "last_updated": "2023-12-31T23:59:59.999999+0000",
            }
        ]
    ],
    indirect=True,
)
def test_format_issue_date(raw_jira_issues):
    assert format_issue_date(raw_jira_issues[0].fields.updated) == date(2023, 12, 31)
