# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS RecordDumpLoader module."""
import importlib_metadata

from cds_ils.importer.errors import RecordNotDeletable, UnknownProvider
from cds_ils.importer.models import ImporterMode


class XMLRecordDumpLoader(object):
    """Load JSON record dump."""

    @classmethod
    def get_importer_class(cls, provider):
        """Load importer for a given provider."""
        try:
            entry_points = importlib_metadata.entry_points()

            # Retrieve the specific entry point for 'console_scripts'
            entry_point = entry_points.select(group="cds_ils.importers")[
                provider
            ].load()
            return entry_point
        except Exception as e:
            raise UnknownProvider

    @classmethod
    def create_json(cls, dump_model):
        """Process the JSON dump."""
        timestamp, json_data, is_deletable = dump_model.dump()
        return json_data, is_deletable

    @classmethod
    def import_from_json(cls, json_data, is_deletable, provider, mode):
        """Import records."""
        importer_class = cls.get_importer_class(provider)

        # ignore the leader XML tag for CDS provider (delete mode indicator),
        # as cds does not include it in the MARCXML
        if provider == "cds" and mode == ImporterMode.DELETE.value:
            is_deletable = True

        if mode == ImporterMode.DELETE.value and not is_deletable:
            raise RecordNotDeletable
        elif mode == ImporterMode.IMPORT.value:
            report = importer_class(json_data, provider).import_record()
        elif mode == ImporterMode.DELETE.value and is_deletable:
            report = importer_class(json_data, provider).delete_record()
        elif mode == ImporterMode.PREVIEW_IMPORT.value:
            report = importer_class(json_data, provider).preview_import()
        elif mode == ImporterMode.PREVIEW_DELETE.value:
            report = importer_class(json_data, provider).preview_delete()
        else:
            report = None
        return report
