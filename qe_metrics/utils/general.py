import os
from typing import Any


from simple_logger.logger import get_logger


LOGGER = get_logger(name="general")


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


def verify_queries(queries_dict: dict[str, str]) -> None:
    """
    Verify that the required queries are present.

    The required queries values are not None in the queries' dictionary.Also verify that there are no other queries other
    than the ones in required_queries.

    Args:
        queries_dict (dict[str, str]): Dictionary holding the queries.

    Raises:
        ValueError: If any of the required queries are missing or the required queries values are None in the queries' dictionary.
                    If there are any queries that are not in the required_queries list.
    """
    required_queries = ["blocker", "critical-blocker"]

    missing_queries = [query for query in required_queries if query not in queries_dict]

    if len(missing_queries) == len(required_queries):
        raise ValueError(f"All queries are missing in the products file: {' '.join(missing_queries)}")
    elif missing_queries:
        LOGGER.warn(f"Some queries is missing in the products file: {' '.join(missing_queries)}")

    if missing_queries := [query for query in required_queries if query not in queries_dict]:
        raise ValueError(f"Missing queries in the products file: {' '.join(missing_queries)}")

    if none_values_queries := [query for query in required_queries if queries_dict.get(query) is None]:
        raise ValueError(f"The following queries have None values: {' '.join(none_values_queries)}")

    if extra_queries := [query for query in queries_dict if query not in required_queries]:
        raise ValueError(f"Extra queries in the products file: {' '.join(extra_queries)}")


def run_in_verbose() -> bool:
    return True if os.environ.get("QE_METRICS_VERBOSE") else False
