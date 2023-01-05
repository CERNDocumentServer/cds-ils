# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

from flask import url_for
from invenio_accounts.testutils import login_user_via_session
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search


def test_ebook_links(app, client, testdata, json_headers, admin):
    """Test ebook links when login_required."""

    # re-index documents to resolve eitems
    ri = RecordIndexer()
    for rec in testdata["documents"]:
        ri.index(rec)
    current_search.flush_and_refresh(index="*")

    def _test_list(endpoint):
        """Get list."""
        url = url_for(endpoint)
        res = client.get(url, headers=json_headers)
        return res.get_json()["hits"]["hits"]

    def _test_read(endpoint, pid):
        """Get record."""
        url = url_for(endpoint, pid_value=pid)
        res = client.get(url, headers=json_headers)
        return res.get_json()

    def _get_item(doc, eitem_pid):
        """Get item from the document record."""
        return [eitem for eitem in doc["eitems"]["hits"] if eitem["pid"] == eitem_pid][
            0
        ]

    def assert_urls(urls):
        """Test urls."""
        protected = urls[0]
        assert protected["login_required"]
        assert protected["value"] == "http://protected-cds-ils.ch/"
        login_required_url = app.config["CDS_ILS_EZPROXY_URL"].format(
            url=protected["value"]
        )
        assert protected["login_required_url"] == login_required_url

        not_protected = urls[1]
        assert not not_protected["login_required"]
        assert not_protected["value"] == "http://cds-ils.ch/"
        assert "login_required_url" not in not_protected

    EITEM_PID = "eitemid-2"
    DOC_PID = "docid-2"
    # documents/literature search endpoint
    for endpoint in [
        "invenio_records_rest.docid_list",
        "invenio_records_rest.litid_list",
    ]:
        records = _test_list(endpoint)
        doc = [r for r in records if r["metadata"]["pid"] == DOC_PID][0]
        eitem = _get_item(doc["metadata"], EITEM_PID)
        assert_urls(eitem["urls"])

    # test doc item endpoint
    doc = _test_read("invenio_records_rest.docid_item", DOC_PID)
    eitem = _get_item(doc["metadata"], EITEM_PID)
    assert_urls(eitem["urls"])

    # eitems endpoint
    login_user_via_session(client, email=admin.email)
    records = _test_list("invenio_records_rest.eitmid_list")
    eitem = [r for r in records if r["metadata"]["pid"] == EITEM_PID][0]
    assert_urls(eitem["metadata"]["urls"])

    eitem = _test_read("invenio_records_rest.eitmid_item", EITEM_PID)
    assert_urls(eitem["metadata"]["urls"])
