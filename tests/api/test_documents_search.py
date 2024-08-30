# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Tests search OR/AND operators.

These tests asserts that when using the AND operator, the `cross_fields`
parameter is required. The `Dreams` word is contained in the `title`, the
`Caroline` word in the author.
The assumption here is that the documents index has the same analyzers
for all searchable fields.
"""

from copy import deepcopy

import pytest
from flask import url_for

from cds_ils import config


@pytest.fixture(scope="module")
def app_config_or(app_config):
    """Change config to use the search OR operator."""

    def and_operator(extra_params={}):
        extra_params["default_operator"] = "OR"

    app_config["RECORDS_REST_ENDPOINTS"] = deepcopy(config.RECORDS_REST_ENDPOINTS)
    app_config["RECORDS_REST_ENDPOINTS"]["docid"]["search_query_parser"] = and_operator
    return app_config


def test_search_or_operator(app_config_or, app, client, testdata, json_headers):
    """Test searching using OR operator."""
    url = url_for("invenio_records_rest.docid_list")
    # test that searching with OR operator will find the document
    response = client.get(f"{url}?q=Dreams%20Caroline", headers=json_headers)
    assert response.status_code == 200
    assert response.get_json()["hits"]["total"] == 1


@pytest.fixture(scope="module")
def app_config_and(app_config):
    """Change config to use the search AND operator."""

    def and_operator(extra_params={}):
        extra_params["default_operator"] = "AND"

    app_config["RECORDS_REST_ENDPOINTS"] = deepcopy(config.RECORDS_REST_ENDPOINTS)
    app_config["RECORDS_REST_ENDPOINTS"]["docid"]["search_query_parser"] = and_operator
    return app_config


def test_search_and_operator(app_config_only_and, app, client, testdata, json_headers):
    """Test searching using AND operator."""
    url = url_for("invenio_records_rest.docid_list")
    # test that searching with AND operator without cross-fields will return 0 results
    response = client.get(f"{url}?q=Dreams%20Caroline", headers=json_headers)
    assert response.status_code == 200
    assert response.get_json()["hits"]["total"] == 0


@pytest.fixture(scope="module")
def app_config_and_cross_fields(app_config):
    """Change config to use the search AND operator and cross_fields."""

    def and_operator(extra_params={}):
        extra_params["default_operator"] = "AND"
        extra_params["type"] = "cross_fields"

    app_config["RECORDS_REST_ENDPOINTS"] = deepcopy(config.RECORDS_REST_ENDPOINTS)
    app_config["RECORDS_REST_ENDPOINTS"]["docid"]["search_query_parser"] = and_operator
    return app_config


def test_search_and_operator(
    app_config_and_cross_fields, app, client, testdata, json_headers
):
    """Test searching using AND operator."""
    url = url_for("invenio_records_rest.docid_list")
    # test that searching with AND operator with cross-fields will return the result
    response = client.get(f"{url}?q=Dreams%20Caroline", headers=json_headers)
    assert response.status_code == 200
    assert response.get_json()["hits"]["total"] == 1
