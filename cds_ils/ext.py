# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS extension."""

from flask import Blueprint
from invenio_records.signals import after_record_insert, after_record_update

from cds_ils.literature.tasks import pick_identifier_with_cover


class CdsIls(object):
    """CdsIls extension."""

    def __init__(self, app=None):
        """Initialization."""
        self.register_signals(app)
        self.init_app(app)

    def init_app(self, app):
        """Initialize app."""
        app.register_blueprint(
            Blueprint("cds_ils", __name__, template_folder="templates")
        )
        app.register_blueprint(
            Blueprint(
                "cds_ils_mail", __name__, template_folder="mail/templates"
            )
        )

    @staticmethod
    def register_signals(app):
        """Register signals."""
        if app.config.get("CDS_ILS_LITERATURE_UPDATE_COVERS", True):
            after_record_insert.connect(pick_identifier_with_cover)
            after_record_update.connect(pick_identifier_with_cover)
