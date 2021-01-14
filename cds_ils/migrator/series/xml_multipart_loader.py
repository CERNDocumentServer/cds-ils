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
from invenio_app_ils.errors import IlsValidationError
from invenio_app_ils.proxies import current_app_ils
from invenio_db import db

from cds_ils.migrator.series.multipart import import_multipart, \
    import_multivolume
from cds_ils.migrator.series.xml_series_loader import CDSSeriesDumpLoader
from cds_ils.migrator.utils import add_cover_metadata, clean_created_by_field

cli_logger = logging.getLogger("migrator")


class CDSMultipartDumpLoader(CDSSeriesDumpLoader):
    """Multipart loader class."""

    @classmethod
    def create_record(cls, dump, rectype):
        """Create a new record from dump."""
        try:
            timestamp, json_data = dump.revisions[-1]
            json_data = clean_created_by_field(json_data)
            add_cover_metadata(json_data)
            is_multivolume_record = json_data["_migration"].get(
                "multivolume_record", False
            )
            if is_multivolume_record:
                click.echo("Multivolume record.")
                record = import_multivolume(json_data)
            else:
                click.echo("Multipart record.")
                record = import_multipart(json_data)
                # the multipart needs to be indexed immediately,
                # because we match them between them
                series_indexer = current_app_ils.series_indexer
                series_indexer.index(record)
                click.echo("Indexing.")
                # wait for the previous multipart to be indexed
                time.sleep(2)
            return record
        except IlsValidationError as e:
            click.secho("Field: {}".format(e.errors[0].res["field"]), fg="red")
            click.secho(e.original_exception.message, fg="red")
            raise e
