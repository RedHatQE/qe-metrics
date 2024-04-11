from typing import Any, Dict, List
from qe_metrics.libs.database_mapping import ProductsEntity
from pyaml_env import parse_config
from pony import orm
from qe_metrics.utils.general import verify_queries
from simple_logger.logger import get_logger

LOGGER = get_logger(name=__name__)


def products_from_file(products_file: str) -> List[Dict[Any, Any]]:
    """
    Initialize the ProductsEntity class from a file. Create new entries if they do not exist.

    Args:
        products_file (str): Path to the yaml file holding product names and their queries

    Returns:
        List[Dict[Any, Any]]: A list of dictionaries that hold the product and its queries
    """
    products_dict = parse_config(path=products_file)
    products = []
    for name, queries in products_dict.items():
        try:
            verify_queries(queries_dict=queries)
            products.append({"product": ProductsEntity.get(name=name) or ProductsEntity(name=name), "queries": queries})
        except ValueError as err:
            LOGGER.error(f"Error occurred parsing queries for product {name}: {err}")
    orm.commit()
    return products


def append_last_updated_arg(query: str, look_back_days: int) -> str:
    """
    Add the last updated argument to the queries.

    Args:
        query (str): Query to be modified
        look_back_days (int): Number of days to look back when querying for issues

    Returns:
        str: A query with an argument to filter issues that have been updated in the last 'look_back_days' days
    """
    if any(word in query for word in ["updatedDate", "updated"]):
        LOGGER.error("Query is already using the 'updatedDate' or 'updated' field. Please remove it:\n{query}")
        return query
    else:
        return f'{query} AND updated > "-{look_back_days}d"'