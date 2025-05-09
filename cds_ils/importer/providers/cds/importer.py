# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS CDS Importer."""
from flask import current_app
from invenio_app_ils.proxies import current_app_ils
from invenio_pidstore.errors import PersistentIdentifierError, PIDDoesNotExistError

from cds_ils.importer.importer import Importer
from cds_ils.literature.api import get_record_by_legacy_recid
from cds_ils.minters import legacy_recid_minter


class CDSImporter(Importer):
    """CDS importer class."""

    UPDATE_DOCUMENT_FIELDS = ("title", "abstract", "authors", "keywords", "urls", "identifiers", "alternative_identifiers", "tags", "_rdm_pid")
    # Mark all CDS elated E-Items as login required and not open access
    EITEM_OPEN_ACCESS = False
    EITEM_URLS_LOGIN_REQUIRED = True

    def _match_document(self):
        """CDS importer match document."""
        document_class = current_app_ils.document_record_cls
        if "_rdm_pid" in self.json_data:
            pid_value = self.json_data["_rdm_pid"]
            external_pid_type = current_app.config["CDS_ILS_RECORD_CDS_RDM_PID_TYPE"]
            try:
                document = get_record_by_legacy_recid(
                    document_class, external_pid_type, pid_value
                )
                return document["pid"], []
            except (PIDDoesNotExistError, PersistentIdentifierError):
                ## we pass to try to match by legacy recid
                pass
        pid_value = self.json_data["legacy_recid"]
        external_pid_type = current_app.config["CDS_ILS_RECORD_LEGACY_PID_TYPE"]
        try:
            document = get_record_by_legacy_recid(
                document_class, external_pid_type, pid_value
            )
        except (PIDDoesNotExistError, PersistentIdentifierError):
            return None, []
        return document["pid"], []

    def import_record(self):
        """Import CDS record with legacy recid."""
        document_class = current_app_ils.document_record_cls
        summary = super().import_record()
        if summary["action"] == "create" and summary["output_pid"]:
            document = document_class.get_record_by_pid(summary["output_pid"])
            record_uuid = document.pid.object_uuid

            if "_rdm_pid" in document:
                external_pid_type = current_app.config[
                    "CDS_ILS_RECORD_CDS_RDM_PID_TYPE"
                ]
                pid_value = document["_rdm_pid"]
            else:
                external_pid_type = current_app.config["CDS_ILS_RECORD_LEGACY_PID_TYPE"]
                pid_value = document["legacy_recid"]
            legacy_recid_minter(
                pid_value,
                external_pid_type,
                record_uuid,
            )
        return summary

    def _extract_eitems_json(self):
        """Extracts eitems json for given pre-processed JSON."""
        eitem = {}

        eitems_external = self.json_data["_migration"]["eitems_external"]
        eitems_proxy = self.json_data["_migration"]["eitems_proxy"]

        if eitems_external:
            eitem = eitems_external[0]
        elif eitems_proxy:
            eitem = eitems_proxy[0]

        if eitem.get("url"):
            eitem["urls"] = [eitem.get("url")]
            del eitem["url"]
        if not eitem.get("urls", []):
            return {}

        open_access = eitem.get("open_access", False)
        internal_notes = eitem.get("internal_notes", "")
        if not open_access:
            eitem["open_access"] = self.json_data["_migration"].get(
                "eitems_open_access", False
            )

        if not internal_notes:
            eitem["internal_notes"] = self.json_data["_migration"][
                "eitems_internal_notes"
            ]

        return eitem
