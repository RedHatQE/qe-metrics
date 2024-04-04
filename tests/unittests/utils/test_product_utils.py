import pytest
from qe_metrics.libs.database_mapping import ProductsEntity
from qe_metrics.utils.product_utils import products_from_file


@pytest.mark.parametrize(
    "tmp_products_file",
    [{"test-from-file-product": {"blocker": "BLOCKER QUERY", "critical-blocker": "CRITICAL BLOCKER QUERY"}}],
    indirect=True,
)
def test_database_products_from_file(db_session, tmp_products_file):
    products_from_file(products_file=tmp_products_file)
    all_products = ProductsEntity.select()
    assert "test-from-file-product" in [
        _product.name for _product in all_products
    ], "Test product test-from-file-product not found in database."
