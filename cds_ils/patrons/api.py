# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Patron api."""

from flask import current_app
from invenio_app_ils.patrons.api import Patron as ILSPatron
from invenio_oauthclient.models import RemoteAccount


class Patron(ILSPatron):
    """Patron record class."""

    _index = "patrons-patron-v1.0.0"
    _doc_type = "patron-v1.0.0"
    # Fake schema used to identify pid type from ES hit
    _schema = "patrons/patron-v1.0.0.json"

    def __init__(self, id, revision_id=None):
        """Create a `Patron` instance."""
        super(Patron, self).__init__(id, revision_id)

        self.extra_info = None
        client_id = current_app.config["CERN_APP_OPENID_CREDENTIALS"][
            "consumer_key"
        ]
        remote_user = RemoteAccount.get(id, client_id)
        if remote_user:
            self.extra_info = remote_user.extra_data

    def dumps(self):
        """Return python representation of Patron metadata."""
        dump = super(Patron, self).dumps()
        if hasattr(self, "extra_info") and self.extra_info:
            dump.update(
                {
                    "person_id": self.extra_info.get("person_id", ""),
                    "department": self.extra_info.get("department", ""),
                }
            )
        return dump
