# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Document Importer module."""
from flask import current_app
from invenio_pidstore.models import PersistentIdentifier

from cds_ils.importer.documents.importer import DocumentImporter
from cds_ils.importer.providers.cds.utils import (
    add_cds_url,
    add_title_from_conference_info,
)
from cds_ils.minters import legacy_recid_minter


class CDSDocumentImporter(DocumentImporter):
    """CDS Document importer class."""

    def _before_create(self):
        """Modify json before creating record."""
        add_title_from_conference_info(self.json_data)
        add_cds_url(self.json_data)
        return super()._before_create()

    def _after_update(self, updated_document):
        if "_rdm_pid" in self.json_data:
            pid = updated_document["pid"]
            _rdm_pid = self.json_data["_rdm_pid"]
            pid_type = "docid"
            pid_obj = PersistentIdentifier.query.filter(
                PersistentIdentifier.pid_value == pid,
                PersistentIdentifier.pid_type == pid_type,
            ).one()

            object_uuid = pid_obj.object_uuid
            rdm_pid_type = current_app.config["CDS_ILS_RECORD_CDS_RDM_PID_TYPE"]
            rdm_pid = PersistentIdentifier.query.filter(
                PersistentIdentifier.object_uuid == object_uuid,
                PersistentIdentifier.pid_type == rdm_pid_type,
            ).one_or_none()

            # if rdm_pid not minted, mint one
            if not rdm_pid:
                legacy_recid_minter(
                    _rdm_pid,
                    rdm_pid_type,
                    object_uuid,
                )
