# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS CDS Importer."""
from cds_ils.importer.importer import Importer


class SNVImporter(Importer):
    """CDS importer class."""

    EITEM_OPEN_ACCESS = False
    EITEM_URLS_LOGIN_REQUIRED = False

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
