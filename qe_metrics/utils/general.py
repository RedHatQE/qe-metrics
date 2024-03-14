from typing import Any

from simple_logger.logger import get_logger


LOGGER = get_logger(name=__name__)


def verify_config(config: dict[str, Any], required_keys: list[str]) -> None:
    """
    Verify that the required keys are present and the required keys values are not None in the config dictionary.

    Args:
        config (dict[str, Any]): Dictionary holding the credentials.
        required_keys (list[str]): List of required keys.

    Raises:
        ValueError: If any of the required keys are missing or the required keys values are None in the config dictionary.
    """
    if missing_keys := [key for key in required_keys if key not in config]:
        raise ValueError(f"Missing keys in the configuration file: {' '.join(missing_keys)}")

    if none_values_keys := [key for key in required_keys if config.get(key) is None]:
        raise ValueError(f"The following keys have None values: {' '.join(none_values_keys)}")
