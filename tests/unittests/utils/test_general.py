import pytest
from qe_metrics.utils.general import verify_config


@pytest.fixture
def valid_config():
    return {"key1": "value1", "key2": "value2"}


@pytest.fixture
def config_none_value():
    return {"key1": "value1", "key2": None}


def test_verify_config_with_all_required_keys_present(valid_config):
    required_keys = ["key1", "key2"]
    verify_config(valid_config, required_keys)


def test_verify_config_with_missing_keys_raises_value_error(valid_config):
    required_keys = ["key1", "key2", "key3"]
    with pytest.raises(ValueError):
        verify_config(valid_config, required_keys)


def test_verify_config_with_none_values_raises_value_error(config_none_value):
    required_keys = ["key1", "key2"]
    with pytest.raises(ValueError):
        verify_config(config_none_value, required_keys)
