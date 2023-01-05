# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS extension."""

from flask import Blueprint
from invenio_indexer.signals import before_record_index
from invenio_records.signals import after_record_insert, after_record_update

from cds_ils.literature.tasks import pick_identifier_with_cover

from .circulation.indexer import index_extra_fields_for_loan


class CdsIls(object):
    """CdsIls extension."""

    def __init__(self, app=None):
        """Initialization."""
        self.register_signals(app)
        self.init_app(app)
        self.init_loan_indexer_hook(app)

    def init_app(self, app):
        """Initialize app."""
        app.register_blueprint(
            Blueprint("cds_ils", __name__, template_folder="templates")
        )
        app.register_blueprint(
            Blueprint(
                "cds_ils_notifications",
                __name__,
                template_folder="notifications/templates",
            )
        )

    @staticmethod
    def register_signals(app):
        """Register signals."""
        if app.config.get("CDS_ILS_LITERATURE_UPDATE_COVERS", True):
            after_record_insert.connect(pick_identifier_with_cover)
            after_record_update.connect(pick_identifier_with_cover)

    def init_loan_indexer_hook(self, app):
        """Custom loan indexer hook init."""
        before_record_index.dynamic_connect(
            before_loan_index_hook,
            sender=app,
            weak=False,
            index="{0}s-{0}-v1.0.0".format("loan"),
        )


def before_loan_index_hook(sender, json=None, record=None, index=None, **kwargs):
    """Hook to transform loan record before ES indexing.

    :param sender: The entity sending the signal.
    :param json: The dumped Record dict which will be indexed.
    :param record: The corresponding Record object.
    :param index: The index in which the json will be indexed.
    :param kwargs: Any other parameters.
    """
    index_extra_fields_for_loan(json)
