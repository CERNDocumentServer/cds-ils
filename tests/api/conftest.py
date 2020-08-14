# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# CDS Books is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Pytest fixtures and plugins for the API application."""

from __future__ import absolute_import, print_function

import pytest
from invenio_app.factory import create_api

from invenio_app_ils.internal_locations.api import INTERNAL_LOCATION_PID_TYPE  # noqa isort:skip
from invenio_app_ils.internal_locations.api import InternalLocation  # noqa isort:skip


@pytest.fixture(scope='module')
def create_app():
    """Create test app."""
    return create_api


@pytest.fixture(scope='module')
def app_config(app_config):
    """Get app config."""
    app_config["APP_ALLOWED_HOSTS"] = ["localhost"]
    app_config["CELERY_TASK_ALWAYS_EAGER"] = True
    app_config["JSONSCHEMAS_SCHEMAS"] = [
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
    ]
    return app_config
