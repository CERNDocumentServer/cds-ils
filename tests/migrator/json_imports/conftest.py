# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Migration pytest fixtures and plugins."""
import time

import pytest
from invenio_app_ils.documents.api import DOCUMENT_PID_TYPE, Document
from invenio_app_ils.internal_locations.api import (
    INTERNAL_LOCATION_PID_TYPE,
    InternalLocation,
)
from invenio_app_ils.items.api import ITEM_PID_TYPE, Item
from invenio_app_ils.locations.api import LOCATION_PID_TYPE, Location
from invenio_app_ils.providers.api import PROVIDER_PID_TYPE, Provider
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search

from cds_ils.migrator.default_records import create_default_records
from cds_ils.patrons.api import Patron
from cds_ils.patrons.indexer import PatronIndexer
from tests.helpers import _create_records, load_json_from_datadir


@pytest.fixture()
def test_data_migration(app, db, es_clear, patrons):
    """Prepare minimal data for migration tests."""
    data = load_json_from_datadir("locations.json")
    locations = _create_records(db, data, Location, LOCATION_PID_TYPE)

    data = load_json_from_datadir("internal_locations.json")
    int_locs = _create_records(db, data, InternalLocation, INTERNAL_LOCATION_PID_TYPE)

    data = load_json_from_datadir("documents.json")
    documents = _create_records(db, data, Document, DOCUMENT_PID_TYPE)

    data = load_json_from_datadir("items.json")
    items = _create_records(db, data, Item, ITEM_PID_TYPE)

    data = load_json_from_datadir("ill_libraries.json")
    ill_libraries = _create_records(db, data, Provider, PROVIDER_PID_TYPE)

    data = load_json_from_datadir("vendors.json")
    vendors = _create_records(db, data, Provider, PROVIDER_PID_TYPE)

    # index
    ri = RecordIndexer()
    for rec in locations + int_locs + documents + items + ill_libraries + vendors:
        ri.index(rec)

    # wait for indexing
    time.sleep(1)
    create_default_records()
    patron = Patron(patrons[0].id)
    PatronIndexer().index(patron)

    current_search.flush_and_refresh(index="*")
