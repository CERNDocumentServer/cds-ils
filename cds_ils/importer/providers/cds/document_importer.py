# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Document Importer module."""
from cds_ils.importer.documents.importer import DocumentImporter
from cds_ils.importer.providers.cds.utils import (
    add_cds_url,
    add_title_from_conference_info,
)


class CDSDocumentImporter(DocumentImporter):
    """CDS Document importer class."""

    def _before_create(self):
        """Modify json before creating record."""
        add_title_from_conference_info(self.json_data)
        add_cds_url(self.json_data)
        return super()._before_create()
