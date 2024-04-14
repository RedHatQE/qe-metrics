import pytest
from qe_metrics.libs.database_mapping import ProductsEntity
from qe_metrics.utils.product_utils import products_from_file, append_last_updated_arg


@pytest.mark.parametrize(
    "tmp_products_file",
    [{"test-from-file-product": {"blocker": "BLOCKER QUERY", "critical-blocker": "CRITICAL BLOCKER QUERY"}}],
    indirect=True,
)
def test_products_from_file(db_session, tmp_products_file):
    products_from_file(products_file=tmp_products_file)
    all_products = ProductsEntity.select()
    assert "test-from-file-product" in [
        _product.name for _product in all_products
    ], "Test product test-from-file-product not found in database."


def test_append_last_updated_arg_appends_arg():
    expected_query = 'project = TEST AND status = Open AND updated > "-90d"'
    query = append_last_updated_arg(query="project = TEST AND status = Open", look_back_days=90)
    assert query == expected_query, f"actual: {query} != expected: {expected_query}"


def test_append_last_updated_arg_not_append_arg():
    query = append_last_updated_arg(query='project = TEST AND status = Open AND updated > "-365d"', look_back_days=90)
    assert not query
