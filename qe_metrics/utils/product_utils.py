from __future__ import annotations
from typing import Any, Dict, List

from concurrent.futures import ThreadPoolExecutor, as_completed
import yaml
from qe_metrics.libs.database_mapping import ProductsEntity
from pyaml_env import parse_config
from qe_metrics.utils.general import verify_queries
from simple_logger.logger import get_logger
from sqlalchemy.orm import Session
import requests

LOGGER = get_logger(name=__name__)


def fetch_config_file_content_from_url(base_url: str, file_name: str) -> requests.Response:
    return requests.get(f"{base_url}/configs/{file_name}")


def products_from_repository() -> Dict[str, Dict[str, str]]:
    config_dict: Dict[str, Dict[str, str]] = {}
    base_url = "https://raw.githubusercontent.com/RedHatQE/qe-metrics-products-config/main"
    product_config_file_url = f"{base_url}/product-config.yaml"
    res = requests.get(product_config_file_url)
    if not res.ok:
        LOGGER.error(f"Failed to fetch products file {product_config_file_url} from repository: {res.status_code}")
        return config_dict

    config_files_content = res.content.decode("utf-8")
    config_files_dict = yaml.safe_load(config_files_content)
    config_files_list: List[str] = config_files_dict.get("configs")
    if not config_files_list:
        LOGGER.error(f"{product_config_file_url} does not contain any config files")
        return config_dict

    futures = []
    with ThreadPoolExecutor() as executor:
        for config_file_name in config_files_list:
            futures.append(executor.submit(fetch_config_file_content_from_url, base_url, config_file_name))

    for result in as_completed(futures):
        if not result.result().ok:
            LOGGER.error(f"Failed to fetch config file {result.result().url}: {result.result().status_code}")
            continue

        config_dict.update(yaml.safe_load(result.result().content.decode("utf-8")))

    return config_dict


def get_products_dict(products_file: str | None = None, products_file_url: bool = False) -> Dict[str, Dict[str, str]]:
    if products_file:
        return parse_config(path=products_file)

    elif products_file_url:
        return products_from_repository()

    LOGGER.error("Either products_file or products_file_url must be set")
    return {}


def process_products(products_dict: Dict[str, Dict[str, str]], db_session: Session) -> List[Dict[Any, Any]]:
    """
    Initialize the ProductsEntity class from a file. Create new entries if they do not exist.

    Args:
        products_dict (Dict[str, Dict[str, str]]): A dictionary that holds the products and their queries
        db_session (Session): SQLAlchemy Session instance.

    Returns:
        List[Dict[Any, Any]]: A list of dictionaries that hold the product and its queries
    """
    products: List[Dict[Any, Any]] = []

    for name, queries in products_dict.items():
        try:
            verify_queries(queries_dict=queries)
            product = db_session.query(ProductsEntity).filter_by(name=name).first()
            if product is None:
                product = ProductsEntity(name=name)
                db_session.add(instance=product)
            products.append({"product": product, "queries": queries})
        except ValueError as err:
            LOGGER.error(f"Error occurred parsing queries for product {name}: {err}")
    db_session.commit()
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
        LOGGER.error(
            f'Query is already using the "updatedDate" or "updated" field. Query will not be executed. \nQuery: "{query}"'
        )
        return ""
    else:
        return f'{query} AND updated > "-{look_back_days}d"'
