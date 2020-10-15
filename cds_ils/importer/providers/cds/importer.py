# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS CDS Importer."""

from cds_ils.importer.documents.api import get_document_by_legacy_recid
from cds_ils.importer.importer import Importer


class CDSImporter(Importer):
    """CDS importer class."""

    def _match(self):
        """CDS importer match document."""
        document = get_document_by_legacy_recid(self.json_data["legacy_recid"])
        return document
