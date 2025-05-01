# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-IlS JSON Importer load module."""

from invenio_db import db

from cds_ils.importer.XMLRecordLoader import XMLRecordDumpLoader


class ILSLoader:
    """Loader class for ETL pattern."""

    def __init__(self, mode, metadata_provider="cds"):
        """Constructor."""
        self.metadata_provider = metadata_provider
        self.update_fields = None
        self.mode = mode
        super().__init__()

    def load(self, entry):
        """Load record based on JSON entry input."""
        try:
            report = XMLRecordDumpLoader.import_from_json(
                entry, True, self.metadata_provider, self.mode
            )
            db.session.commit()
            return report
        except Exception as e:
            db.session.rollback()
            raise e
