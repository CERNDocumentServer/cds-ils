# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Test loan migration."""
import os
import time

import pytest
from invenio_app_ils.circulation.indexer import LoanIndexer
from invenio_circulation.api import Loan
from invenio_circulation.proxies import current_circulation
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_search import current_search

from cds_ils.migrator.errors import LoanMigrationError
from cds_ils.migrator.loans.api import import_loans_from_json


def reindex_loans():
    query = (x[0] for x in PersistentIdentifier.query.filter_by(
        object_type='rec', status=PIDStatus.REGISTERED
    ).filter(
        PersistentIdentifier.pid_type.in_(("loanid",))
    ).values(
        PersistentIdentifier.pid_value
    ))

    for loan_pid in query:
        LoanIndexer().index(Loan.get_record_by_pid(loan_pid))


def test_import_loan_returned(test_data_migration, legacy_borrower_id,
                              es_clear):
    datadir = os.path.join(os.path.dirname(__file__), "data")
    file = (open(os.path.join(datadir, "loans.json"), "r"),)
    import_loans_from_json(file)
    reindex_loans()
    current_search.flush_and_refresh(index="*")
    LoanSearch = current_circulation.loan_search_cls
    search = (
        LoanSearch()
            .filter("term", document_pid="docid-1")
            .filter("term", state="ITEM_RETURNED")
    )
    results = search.execute()

    assert results.hits.total.value == 1
    assert results[0].start_date == "2010-09-29T00:00:00"

    search = (
        LoanSearch()
            .filter("term", document_pid="docid-1")
            .filter("term", state="ITEM_ON_LOAN")
            .filter("term", item_pid__value="itemid-1")
    )
    results = search.execute()
    assert results.hits.total.value == 1
    assert results[0].start_date == "2009-07-07T00:00:00"


def test_import_invalid_loan(testdata):
    datadir = os.path.join(os.path.dirname(__file__), "data")
    file = (
        open(os.path.join(datadir, "loan_ongoing_anonymous_user.json"), "r"),
    )

    with pytest.raises(LoanMigrationError):
        import_loans_from_json(file, raise_exceptions=True)