import os

import pytest
from invenio_app_ils.acquisition.api import ORDER_PID_TYPE
from invenio_app_ils.acquisition.proxies import current_ils_acq
from invenio_search import current_search

from cds_ils.migrator.acquisition.orders import import_orders_from_json
from cds_ils.migrator.errors import AcqOrderError
from tests.migrator.utils import reindex_record


def test_import_orders(test_data_migration, patrons, es_clear):
    datadir = os.path.join(os.path.dirname(__file__), "data")
    file = open(os.path.join(datadir, "orders.json"), "r")
    import_orders_from_json(file)

    reindex_record(
        ORDER_PID_TYPE, current_ils_acq.order_record_cls, current_ils_acq.order_indexer
    )

    current_search.flush_and_refresh(index="*")

    order_search = current_ils_acq.order_search_cls

    search = order_search().filter("term", legacy_id="30747")

    results = search.execute()

    assert results.hits.total.value == 1
    assert results[0].status == "RECEIVED"

    search = order_search().filter("term", legacy_id="56277")
    results = search.execute()
    assert results.hits.total.value == 1

    assert results[0].status == "ORDERED"
    file.close()


def test_import_invalid_loan(test_data_migration):
    datadir = os.path.join(os.path.dirname(__file__), "data")
    file = open(os.path.join(datadir, "invalid_order.json"), "r")

    with pytest.raises(AcqOrderError):
        import_orders_from_json(file, raise_exceptions=True)
    file.close()
