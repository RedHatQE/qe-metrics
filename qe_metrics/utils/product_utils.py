from typing import List
from qe_metrics.libs.database_mapping import ProductsEntity
from pyaml_env import parse_config
from pony import orm
from qe_metrics.utils.general import verify_queries

def products_from_file(products_file: str) -> List["ProductsEntity"]:
    """
    Initialize the ProductsEntity class from a file. Create new entries if they do not exist. Update the queries if
    they are modified.

    Args:
        products_file (str): Path to the yaml file holding product names and their queries

    Returns:
        List["ProductsEntity"]: A list of Products objects
    """
    products_dict = parse_config(path=products_file)
    products = []
    for name, queries in products_dict.items():
        verify_queries(queries_dict=queries)
        if not (product := ProductsEntity.get(name=name)):
            products.append(ProductsEntity(name=name, queries=queries))
        else:
            setattr(product, "queries", queries)
            products.append(product)
    orm.commit()
    return products