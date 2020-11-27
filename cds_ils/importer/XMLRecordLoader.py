# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS RecordDumpLoader module."""
import pkg_resources

from cds_ils.importer.errors import RecordNotDeletable


class XMLRecordDumpLoader(object):
    """Load JSON record dump."""

    @classmethod
    def get_importer_class(cls, provider):
        """Load importer for a given provider."""
        return pkg_resources.load_entry_point(
            "cds-ils", "cds_ils.importers", provider
        )

    @classmethod
    def process(cls, dump_model, provider, mode):
        """Process the JSON dump."""
        timestamp, json_data, is_deletable = dump_model.dump()
        importer_class = cls.get_importer_class(provider)
        if mode == "delete" and not is_deletable:
            raise RecordNotDeletable()
        if mode == "create":
            report = importer_class(json_data, provider).import_record()
        elif mode == "delete" and is_deletable:
            report = importer_class(json_data, provider).delete_record()
        return report
