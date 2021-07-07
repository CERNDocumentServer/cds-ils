# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS CDS Importer."""
from flask import current_app
from invenio_app_ils.proxies import current_app_ils

from cds_ils.importer.importer import Importer
from cds_ils.literature.api import get_record_by_legacy_recid


class CDSImporter(Importer):
    """CDS importer class."""

    def _match_document(self):
        """CDS importer match document."""
        legacy_pid_type = current_app.config["CDS_ILS_RECORD_LEGACY_PID_TYPE"]
        document_class = current_app_ils.document_record_cls
        document = get_record_by_legacy_recid(
            document_class, legacy_pid_type, self.json_data["legacy_recid"]
        )
        return document
