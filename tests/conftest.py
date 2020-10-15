# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Common pytest fixtures and plugins."""
from __future__ import absolute_import, print_function

import pytest
from invenio_access import ActionRoles, superuser_access
from invenio_accounts.models import Role, User
from invenio_app.factory import create_api
from invenio_app_ils.documents.api import DOCUMENT_PID_TYPE, Document
from invenio_app_ils.eitems.api import EITEM_PID_TYPE, EItem
from invenio_app_ils.internal_locations.api import \
    INTERNAL_LOCATION_PID_TYPE, InternalLocation
from invenio_app_ils.items.api import ITEM_PID_TYPE, Item
from invenio_app_ils.locations.api import LOCATION_PID_TYPE, Location
from invenio_app_ils.series.api import SERIES_PID_TYPE, Series
from invenio_circulation.api import Loan
from invenio_circulation.pidstore.pids import CIRCULATION_LOAN_PID_TYPE
from invenio_indexer.api import RecordIndexer
from invenio_oauthclient.models import RemoteAccount, UserIdentity
from invenio_search import current_search
from invenio_userprofiles.models import UserProfile

from .helpers import _create_records, load_json_from_datadir


@pytest.fixture(scope="module")
def create_app():
    """Create test app."""
    return create_api


@pytest.fixture(scope="module")
def app_config(app_config):
    """Get app config."""
    tests_config = {
        "APP_ALLOWED_HOSTS": "localhost",
        "CELERY_TASK_ALWAYS_EAGER": True,
        "CDS_ILS_LITERATURE_UPDATE_COVERS": False,
        "EXTEND_LOANS_LOCATION_UPDATED": False,
        "JSONSCHEMAS_SCHEMAS": [
            "acquisition",
            "document_requests",
            "documents",
            "eitems",
            "ill",
            "internal_locations",
            "items",
            "invenio_opendefinition",
            "invenio_records_files",
            "loans",
            "locations",
            "series",
            "vocabularies",
        ],
    }
    app_config.update(tests_config)
    return app_config


@pytest.fixture()
def json_headers():
    """JSON headers."""
    return [
        ("Content-Type", "application/json"),
        ("Accept", "application/json"),
    ]


@pytest.fixture()
def admin(app, db):
    """Create admin, librarians and patrons."""
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        admin = datastore.create_user(
            email="admin@test.com", password="123456", active=True
        )
        # Give role to admin
        admin_role = Role(name="admin")
        db.session.add(
            ActionRoles(action=superuser_access.value, role=admin_role)
        )
        datastore.add_role_to_user(admin, admin_role)
    db.session.commit()

    return admin


@pytest.fixture()
def patron1(app, db):
    """Create a patron user."""
    user = User(**dict(email="patron1@cern.ch", active=True))
    db.session.add(user)
    db.session.commit()

    user_id = user.id

    identity = UserIdentity(**dict(id="1", method="cern", id_user=user_id))
    db.session.add(identity)

    profile = UserProfile(
        **dict(
            user_id=user_id,
            _displayname="id_" + str(user_id),
            full_name="System User",
        )
    )
    db.session.add(profile)

    client_id = app.config["CERN_APP_OPENID_CREDENTIALS"]["consumer_key"]
    remote_account = RemoteAccount(
        client_id=client_id,
        **dict(
            user_id=user_id,
            extra_data=dict(person_id="1", department="Department"),
        )
    )
    db.session.add(remote_account)
    db.session.commit()
    return user


@pytest.fixture()
def testdata(app, db, es_clear, patron1):
    """Create, index and return test data."""
    data = load_json_from_datadir("locations.json")
    locations = _create_records(db, data, Location, LOCATION_PID_TYPE)

    data = load_json_from_datadir("internal_locations.json")
    int_locs = _create_records(
        db, data, InternalLocation, INTERNAL_LOCATION_PID_TYPE
    )

    data = load_json_from_datadir("documents.json")
    documents = _create_records(db, data, Document, DOCUMENT_PID_TYPE)

    data = load_json_from_datadir("series.json")
    series = _create_records(db, data, Series, SERIES_PID_TYPE)

    data = load_json_from_datadir("items.json")
    items = _create_records(db, data, Item, ITEM_PID_TYPE)

    data = load_json_from_datadir("eitems.json")
    eitems = _create_records(db, data, EItem, EITEM_PID_TYPE)

    data = load_json_from_datadir("loans.json")
    loans = _create_records(db, data, Loan, CIRCULATION_LOAN_PID_TYPE)

    # index
    ri = RecordIndexer()
    for rec in (
        locations + int_locs + series + documents + items + eitems + loans
    ):
        ri.index(rec)

    current_search.flush_and_refresh(index="*")
    return {
        "documents": documents,
        "eitems": eitems,
        "internal_locations": int_locs,
        "items": items,
        "loans": loans,
        "locations": locations,
        "series": series,
    }
