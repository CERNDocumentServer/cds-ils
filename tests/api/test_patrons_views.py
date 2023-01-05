# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

from flask import url_for
from invenio_access.models import ActionUsers
from invenio_accounts.testutils import login_user_via_session
from invenio_app_ils.patrons.indexer import PatronIndexer
from invenio_db import db
from invenio_search import current_search

from cds_ils.patrons.api import Patron
from cds_ils.patrons.permissions import retrieve_patron_loans_access_action


def test_patron_loans_view(app, patrons, testdata, client):
    """Test check for users update in sync command."""
    patron1 = patrons[0]
    db.session.add(ActionUsers.allow(retrieve_patron_loans_access_action, user=patron1))
    db.session.commit()

    patron = Patron(patron1.id)
    PatronIndexer().index(patron)
    current_search.flush_and_refresh(index="*")

    login_user_via_session(client, email=patron1.email)

    resp = client.get(url_for("cds_ils_patron_loans.patron_loans", person_id=1))

    assert resp.status_code == 200

    expected_literature_on_loan = [
        {
            "item": {
                "barcode": "123456789-3",
                "pid": {
                    "type": "pitmid",
                    "value": "itemid-2",
                },
            },
            "start_date": "2018-06-28",
            "end_date": "2018-07-28",
            "title": "Prairie Fires: The American Dreams of " "Laura Ingalls Wilder",
        },
        {
            "item": {
                "barcode": "",
                "pid": {
                    "type": "illbid",
                    "value": "illbid-1",
                },
            },
            "start_date": "2018-06-28",
            "end_date": "2018-07-28",
            "title": "The Gulf: The Making of An American Sea",
        },
    ]
    expected_loan_requests = [
        {
            "request_start_date": "2018-06-28",
            "request_end_date": "2018-07-28",
            "title": "The Gulf: The Making of An American Sea",
        }
    ]
    data = resp.json
    assert data["on_loan"] == expected_literature_on_loan
    assert data["requests"] == expected_loan_requests

    # test extra_info
    assert patron.extra_info
    assert data["person_id"] == patron.extra_info["person_id"]
    assert data["department"] == patron.extra_info["department"]
