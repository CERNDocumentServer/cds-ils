# Copyright (C) 2024 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

from flask import url_for


def test_search_multiple_fields_with_cross_fields(app, client, testdata, json_headers):
    """Test searching documents with keywords in multiple fields."""
    url = url_for("invenio_records_rest.docid_list")
    response = client.get(f"{url}?q=american%20caroline", headers=json_headers)

    assert response.status_code == 200
    result = response.get_json()
    assert result["hits"]["total"] == 2


def _query_params_modifier(extra_params):
    extra_params["default_operator"] = "AND"
    extra_params["type"] = "cross_fields"


def test_search_multiple_fields_with_and(app, client, testdata, json_headers):
    """Test searching documents with keywords in multi fields with default_operator AND"""
    app.config["RECORDS_REST_ENDPOINTS"]["docid"][
        "search_query_parser"
    ] = _query_params_modifier

    url = url_for("invenio_records_rest.docid_list")
    response = client.get(f"{url}?q=american%20caroline", headers=json_headers)

    assert response.status_code == 200
    result = response.get_json()
    assert result["hits"]["total"] == 0
