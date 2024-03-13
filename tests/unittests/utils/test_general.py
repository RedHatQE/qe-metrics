import pytest
from qe_metrics.utils.general import verify_creds


@pytest.fixture
def valid_creds():
    return {"key1": "value1", "key2": "value2"}


@pytest.fixture
def creds_none_value():
    return {"key1": "value1", "key2": None}


def test_verify_creds_with_all_required_keys_present(valid_creds):
    required_keys = ["key1", "key2"]
    verify_creds(valid_creds, required_keys)


def test_verify_creds_with_missing_keys_raises_value_error(valid_creds):
    required_keys = ["key1", "key2", "key3"]
    with pytest.raises(ValueError):
        verify_creds(valid_creds, required_keys)


def test_verify_creds_with_none_values_raises_value_error(creds_none_value):
    required_keys = ["key1", "key2"]
    with pytest.raises(ValueError):
        verify_creds(creds_none_value, required_keys)
