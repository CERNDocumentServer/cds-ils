# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS CDS Importer."""
from invenio_app_ils.proxies import current_app_ils

from cds_ils.importer.importer import Importer
from cds_ils.literature.api import get_record_by_legacy_recid


class CDSImporter(Importer):
    """CDS importer class."""

    def _match(self):
        """CDS importer match document."""
        document_class = current_app_ils.document_record_cls
        document = get_record_by_legacy_recid(
            document_class, self.json_data["legacy_recid"]
        )
        return document
