# Copyright (C) 2024 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

from flask import url_for


def test_search_multiple_fields(app, client, testdata, json_headers):
    """Test searching documents with keywords in multiple fields."""
    url = url_for("invenio_records_rest.docid_list")
    response = client.get(f"{url}?q=american%20caroline", headers=json_headers)
    assert response.status_code == 200
    print(response.get_json())
    # fix me: assert that in the response we should have at least one hit, and the
    # document with the `docid-2`
    # add a second test that should fail if `type: cross_field` is removed from the
    # search config.
