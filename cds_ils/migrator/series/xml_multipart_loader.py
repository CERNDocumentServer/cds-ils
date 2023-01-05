# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Migrator Records loader."""

import logging
import time

import click

from cds_ils.importer.series.importer import VOCABULARIES_FIELDS
from cds_ils.importer.vocabularies_validator import validator as vocabulary_validator
from cds_ils.migrator.series.multipart import import_multipart, import_multivolume
from cds_ils.migrator.series.xml_series_loader import CDSSeriesDumpLoader
from cds_ils.migrator.utils import add_cover_metadata, clean_created_by_field

cli_logger = logging.getLogger("migrator")


class CDSMultipartDumpLoader(CDSSeriesDumpLoader):
    """Multipart loader class."""

    @classmethod
    def create_record(cls, dump, rectype):
        """Create a new record from dump."""
        timestamp, json_data = dump.revisions[-1]
        json_data = clean_created_by_field(json_data)
        vocabulary_validator.validate(VOCABULARIES_FIELDS, json_data)

        add_cover_metadata(json_data)
        is_multivolume_record = json_data["_migration"].get("multivolume_record", False)

        if is_multivolume_record:
            click.echo("Multivolume record.")
            record = import_multivolume(json_data)
        else:
            click.echo("Multipart record.")
            record = import_multipart(json_data)
            # wait for the previous multipart to be indexed
            click.echo("Indexing.")
            time.sleep(2)
        return record
