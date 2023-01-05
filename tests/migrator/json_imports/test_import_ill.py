import os

import pytest
from invenio_app_ils.ill.api import BORROWING_REQUEST_PID_TYPE
from invenio_app_ils.ill.proxies import current_ils_ill
from invenio_circulation.proxies import current_circulation
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search

from cds_ils.migrator.errors import BorrowingRequestError
from cds_ils.migrator.ill.api import import_ill_borrowing_requests_from_json
from tests.migrator.utils import reindex_record


def test_import_ills(test_data_migration, patrons, es_clear):
    datadir = os.path.join(os.path.dirname(__file__), "data")
    file = open(os.path.join(datadir, "ills.json"), "r")

    import_ill_borrowing_requests_from_json(file)

    reindex_record(
        BORROWING_REQUEST_PID_TYPE,
        current_ils_ill.borrowing_request_record_cls,
        RecordIndexer(),
    )

    current_search.flush_and_refresh(index="*")

    brw_search = current_ils_ill.borrowing_request_search_cls

    search = brw_search().filter("term", legacy_id="1")

    results = search.execute()

    assert results.hits.total.value == 1
    assert results[0].status == "RETURNED"
    assert (
        results[0].notes == "request type: book\n\n"
        "due date: 2010-09-17T00:00:00\n\n"
        "cost: 0 EUR\n\n"
        "item info: {'publisher': '', 'isbn': '',"
        " 'title': \"Documentation Eaux usées et Stations d'épuration\", "
        "'authors': '', 'edition': '', 'place': '', 'year': ''}"
        "\n\nlibrary notes: {}\n"
    )

    ill_pid = results[0].pid
    # make sure no loan created for finished ILLs
    loan_search = current_circulation.loan_search_cls
    search = (
        loan_search()
        .filter("term", item_pid__value=ill_pid)
        .filter("term", item_pid__type=BORROWING_REQUEST_PID_TYPE)
        .filter("term", state="ITEM_ON_LOAN")
    )
    results = search.execute()
    assert results.hits.total.value == 0

    search = brw_search().filter("term", legacy_id="55930")
    results = search.execute()
    assert results.hits.total.value == 1

    expected = (
        "request type: book\n\n"
        "due date: 2021-01-04T00:00:00\n\n"
        "cost: CHF 11.15\n\n"
        "item info: {'publisher': '', 'isbn': '', "
        "'title': '', 'authors': 'A. Agüero, J.M. Albella', "
        "'edition': '', 'place': '', 'year': ''}\n\n"
        "library notes: {'2010-09-28 10:40:50': "
        '"Il libro non e disponibile in italiano, '
        'cancellata: la civiltà."}\n'
    )
    assert results[0].notes == expected

    assert results[0].status == "ON_LOAN"
    ill_pid = results[0].pid

    # check if loan created for ongoing ILL
    loan_search = current_circulation.loan_search_cls
    search = (
        loan_search()
        .filter("term", item_pid__value=ill_pid)
        .filter("term", item_pid__type=BORROWING_REQUEST_PID_TYPE)
        .filter("term", state="ITEM_ON_LOAN")
    )
    results = search.execute()
    assert results.hits.total.value == 1

    file.close()


def test_import_invalid_loan(test_data_migration):
    datadir = os.path.join(os.path.dirname(__file__), "data")
    file = open(os.path.join(datadir, "invalid_ill.json"), "r")

    with pytest.raises(BorrowingRequestError):
        import_ill_borrowing_requests_from_json(file, raise_exceptions=True)

    file.close()
