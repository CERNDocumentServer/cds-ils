# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Patron api."""

from flask import current_app
from invenio_app_ils.patrons.api import AnonymousPatron as ILSAnonymousPatron
from invenio_app_ils.patrons.api import Patron as ILSPatron
from invenio_oauthclient.models import RemoteAccount


class Patron(ILSPatron):
    """Patron record class."""

    def __init__(self, id, revision_id=None):
        """Create a `Patron` instance."""
        super().__init__(id, revision_id)

        self.extra_info = None
        client_id = current_app.config["CERN_APP_OPENID_CREDENTIALS"]["consumer_key"]
        remote_user = RemoteAccount.get(id, client_id)
        if remote_user:
            self.extra_info = remote_user.extra_data

    def _add_extra_info(self, dump):
        """Add extra info when dumping."""
        if hasattr(self, "extra_info") and self.extra_info:
            dump.update(
                {
                    "person_id": str(self.extra_info.get("person_id", "")),
                    "department": self.extra_info.get("department", ""),
                    "legacy_id": str(self.extra_info.get("legacy_id", "")),
                    "mailbox": str(self.extra_info.get("mailbox", "")),
                }
            )

    def dumps(self):
        """Return python representation of Patron metadata."""
        dump = super().dumps()
        self._add_extra_info(dump)
        return dump

    def dumps_loader(self, **kwargs):
        """Return a simpler patron representation for loaders."""
        dump = super().dumps_loader()
        self._add_extra_info(dump)
        return dump


class AnonymousPatron(ILSAnonymousPatron):
    """Anonymous patron record class."""

    def _add_extra_info(self, dump):
        """Add extra info when dumping."""
        dump.update(
            {
                "person_id": "anonymous",
                "department": "anonymous",
                "legacy_id": "anonymous",
                "mailbox": "anonymous",
            }
        )

    def dumps(self):
        """Return python representation of metadata."""
        dump = super().dumps()
        self._add_extra_info(dump)
        return dump

    def dumps_loader(self, **kwargs):
        """Return a simpler representation for loaders."""
        dump = super().dumps_loader()
        self._add_extra_info(dump)
        return dump
