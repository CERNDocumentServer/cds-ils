# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer pytest fixtures and plugins."""
import pytest
from invenio_app_ils.documents.api import DOCUMENT_PID_TYPE
from invenio_app_ils.eitems.api import EITEM_PID_TYPE, EItem
from invenio_app_ils.proxies import current_app_ils
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search

from ..helpers import _create_records, load_json_from_datadir


@pytest.fixture(scope="function")
def importer_test_data(app, db, es_clear):
    """Provide test data for importer test suite."""
    data = load_json_from_datadir(
        "existing_documents.json", relpath="importer"
    )
    Document = current_app_ils.document_record_cls
    documents = _create_records(db, data, Document, DOCUMENT_PID_TYPE)

    data = load_json_from_datadir("existing_eitems.json", relpath="importer")
    eitems = _create_records(db, data, EItem, EITEM_PID_TYPE)

    # index
    ri = RecordIndexer()
    for rec in documents + eitems:
        ri.index(rec)

    current_search.flush_and_refresh(index="*")

    return {"documents": documents, "eitems": eitems}
