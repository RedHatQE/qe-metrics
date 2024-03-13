from typing import Any

from simple_logger.logger import get_logger


LOGGER = get_logger(name=__name__)


def verify_creds(creds: dict[str, Any], required_keys: list[str]) -> None:
    """
    Verify that the required keys are present in the creds dictionary.

    Args:
        creds (dict[str, Any]): Dictionary holding the credentials.
        required_keys (list[str]): List of required keys.

    Raises:
        ValueError: If any of the required keys are missing in the creds dictionary.
    """
    if missing_keys := [key for key in required_keys if key not in creds]:
        raise ValueError(f"Missing keys in the configuration file: {' '.join(missing_keys)}")
