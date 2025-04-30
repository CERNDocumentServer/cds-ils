# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer module."""

import importlib_metadata

from cds_ils.importer.json.errors import ImporterException
from cds_ils.importer.json.load import ILSLoader


class JSONImporter:
    """JSON Generic importer class."""

    def __init__(self, provider):
        self.provider = provider
        super().__init__()

    def get_transformer(self):
        """Determine which document importer to use."""
        try:
            entry_points = importlib_metadata.entry_points()
            return entry_points.select(
                group="cds_ils.importer.import_json_transformers"
            )[self.provider].load()
        except Exception as e:
            raise ImporterException(description="Improper importer configuration.")

    def run(self, data, mode):
        """Run import."""
        transformer = self.get_transformer()
        ils_entry = transformer(data).transform()
        loader = ILSLoader(mode)
        report = loader.load(ils_entry)
        return report
