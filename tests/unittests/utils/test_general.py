import pytest
from qe_metrics.utils.general import verify_creds


@pytest.fixture
def creds():
    return {"key1": "value1", "key2": "value2"}


def test_verify_creds_with_all_required_keys_present(creds):
    required_keys = ["key1", "key2"]
    verify_creds(creds, required_keys)


def test_verify_creds_with_missing_keys_raises_value_error(creds):
    required_keys = ["key1", "key2", "key3"]
    with pytest.raises(ValueError):
        verify_creds(creds, required_keys)
