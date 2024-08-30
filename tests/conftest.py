# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Common pytest fixtures and plugins."""

import os

import jinja2
import pytest
from flask import Blueprint
from invenio_access.models import ActionRoles
from invenio_access.permissions import superuser_access
from invenio_accounts.models import Role, User
from invenio_app.factory import create_api
from invenio_app_ils.documents.api import DOCUMENT_PID_TYPE, Document
from invenio_app_ils.eitems.api import EITEM_PID_TYPE, EItem
from invenio_app_ils.ill.api import BORROWING_REQUEST_PID_TYPE, BorrowingRequest
from invenio_app_ils.internal_locations.api import (
    INTERNAL_LOCATION_PID_TYPE,
    InternalLocation,
)
from invenio_app_ils.items.api import ITEM_PID_TYPE, Item
from invenio_app_ils.locations.api import LOCATION_PID_TYPE, Location
from invenio_app_ils.providers.api import PROVIDER_PID_TYPE, Provider
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
        "MAIL_NOTIFY_SENDER": "sender@test.com",
        "ILS_MAIL_NOTIFY_MANAGEMENT_RECIPIENTS": ["internal@test.com"],
        "CDS_ILS_LITERATURE_UPDATE_COVERS": False,
        "SQLALCHEMY_DATABASE_URI": "postgresql+psycopg2://invenio:invenio@localhost/invenio",
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
            "providers",
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
        db.session.add(ActionRoles(action=superuser_access.value, role=admin_role))
        datastore.add_role_to_user(admin, admin_role)
    db.session.commit()

    return admin


@pytest.fixture()
def patrons(app, db):
    """Create a patron user."""
    db.session.execute("ALTER SEQUENCE IF EXISTS accounts_user_id_seq RESTART")
    db.session.commit()

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
            full_name="USER, System",
        )
    )
    db.session.add(profile)

    client_id = app.config["CERN_APP_OPENID_CREDENTIALS"]["consumer_key"]
    remote_account = RemoteAccount(
        client_id=client_id,
        **dict(
            user_id=user_id,
            extra_data=dict(person_id="1", department="Department", legacy_id="1"),
        )
    )
    db.session.add(remote_account)
    db.session.commit()

    user2 = User(**dict(email="patron2@cern.ch", active=True))
    db.session.add(user2)
    db.session.commit()

    user2_id = user2.id

    profile = UserProfile(
        **dict(
            user_id=user2_id,
            _displayname="id_" + str(user2_id),
            full_name="USER, System",
        )
    )
    db.session.add(profile)
    db.session.commit()

    return user, user2


@pytest.fixture()
def testdata(app, db, es_clear, patrons):
    """Create, index and return test data."""
    data = load_json_from_datadir("locations.json")
    locations = _create_records(db, data, Location, LOCATION_PID_TYPE)

    data = load_json_from_datadir("internal_locations.json")
    int_locs = _create_records(db, data, InternalLocation, INTERNAL_LOCATION_PID_TYPE)

    data = load_json_from_datadir("documents.json")
    documents = _create_records(db, data, Document, DOCUMENT_PID_TYPE)

    data = load_json_from_datadir("series.json")
    series = _create_records(db, data, Series, SERIES_PID_TYPE)

    data = load_json_from_datadir("items.json")
    items = _create_records(db, data, Item, ITEM_PID_TYPE)

    data = load_json_from_datadir("eitems.json")
    eitems = _create_records(db, data, EItem, EITEM_PID_TYPE)

    data = load_json_from_datadir("ill_libraries.json")
    ill_libraries = _create_records(db, data, Provider, PROVIDER_PID_TYPE)

    data = load_json_from_datadir("ill_borrowing_requests.json")
    ill_brw_reqs = _create_records(
        db, data, BorrowingRequest, BORROWING_REQUEST_PID_TYPE
    )

    data = load_json_from_datadir("loans.json")
    loans = _create_records(db, data, Loan, CIRCULATION_LOAN_PID_TYPE)

    # index
    ri = RecordIndexer()
    for rec in (
        locations
        + int_locs
        + series
        + documents
        + items
        + eitems
        + loans
        + ill_libraries
        + ill_brw_reqs
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


@pytest.fixture(scope="module")
def app_with_notifs(app):
    """App with notifications test templates."""
    app.register_blueprint(
        Blueprint("invenio_app_ils_tests", __name__, template_folder="templates")
    )
    # add extra test templates to the search app blueprint, to fake the
    # existence of `invenio-theme` base templates.
    test_templates_path = os.path.join(os.path.dirname(__file__), "templates")
    enhanced_jinja_loader = jinja2.ChoiceLoader(
        [
            app.jinja_loader,
            jinja2.FileSystemLoader(test_templates_path),
        ]
    )
    # override default app jinja_loader to add the new path
    app.jinja_loader = enhanced_jinja_loader
    yield app
