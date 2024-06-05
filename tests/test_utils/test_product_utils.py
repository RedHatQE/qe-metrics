import pytest
from sqlalchemy import select
from qe_metrics.libs.database_mapping import ProductsEntity
from qe_metrics.utils.product_utils import get_products_dict, process_products, append_last_updated_arg


@pytest.mark.parametrize(
    "tmp_products_file",
    [{"test-from-file-product": {"blocker": "BLOCKER QUERY", "critical-blocker": "CRITICAL BLOCKER QUERY"}}],
    indirect=True,
)
def test_products_from_file(tmp_products_file, db_session):
    process_products(products_dict=get_products_dict(products_file=tmp_products_file), db_session=db_session)
    assert "test-from-file-product" in [
        _product.name for _product in db_session.execute(select(ProductsEntity)).scalars()
    ], "Test product test-from-file-product not found in database."


def test_append_last_updated_arg_appends_arg():
    expected_query = 'project = TEST AND status = Open AND updated > "-90d"'
    query = append_last_updated_arg(query="project = TEST AND status = Open", look_back_days=90)
    assert query == expected_query, f"actual: {query} != expected: {expected_query}"


def test_append_last_updated_arg_not_append_arg():
    query = append_last_updated_arg(query='project = TEST AND status = Open AND updated > "-365d"', look_back_days=90)
    assert not query
