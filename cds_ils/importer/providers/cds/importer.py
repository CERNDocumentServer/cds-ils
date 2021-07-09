# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS CDS Importer."""
from flask import current_app
from invenio_app_ils.proxies import current_app_ils
from invenio_pidstore.errors import PIDDoesNotExistError, \
    PersistentIdentifierError

from cds_ils.importer.importer import Importer
from cds_ils.literature.api import get_record_by_legacy_recid
from cds_ils.minters import legacy_recid_minter


class CDSImporter(Importer):
    """CDS importer class."""

    def _match_document(self):
        """CDS importer match document."""
        legacy_pid_type = current_app.config["CDS_ILS_RECORD_LEGACY_PID_TYPE"]
        document_class = current_app_ils.document_record_cls
        try:
            document = get_record_by_legacy_recid(
                document_class, legacy_pid_type, self.json_data["legacy_recid"]
            )
        except (PIDDoesNotExistError, PersistentIdentifierError):
            return
        return document

    def import_record(self):
        summary = super().import_record()
        if self.action == "create" and self.document:
            legacy_pid_type = current_app.config[
                "CDS_ILS_RECORD_LEGACY_PID_TYPE"
            ]
            record_uuid = self.document.pid.object_uuid

            legacy_recid_minter(
                self.document["legacy_recid"], legacy_pid_type, record_uuid
            )
        return summary


