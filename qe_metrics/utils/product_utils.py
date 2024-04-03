from typing import Any, Dict, List
from qe_metrics.libs.database_mapping import ProductsEntity
from pyaml_env import parse_config
from pony import orm
from qe_metrics.utils.general import verify_queries


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
        verify_queries(queries_dict=queries)
        products.append({"product": ProductsEntity.get(name=name) or ProductsEntity(name=name), "queries": queries})
    orm.commit()
    return products
