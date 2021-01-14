# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator."""

import json
import logging

import click
from invenio_app_ils.errors import IlsValidationError
from invenio_db import db

from cds_ils.importer.api import import_record
from cds_ils.migrator.series import journal_marc21, mutlipart_marc21, \
    serial_marc21
from cds_ils.migrator.series.xml_series_loader import CDSSeriesDumpLoader
from cds_ils.migrator.utils import model_provider_by_rectype
from cds_ils.migrator.xml_to_json_dump import CDSRecordDump

migrated_logger = logging.getLogger("migrated_records")
records_logger = logging.getLogger("records_errored")


def import_series_from_dump(
    sources, rectype, loader_class=CDSSeriesDumpLoader
):
    """Load serial records from given sources."""
    if rectype == "serial":
        dojson_model = serial_marc21
    elif rectype == "multipart":
        dojson_model = mutlipart_marc21
    else:
        dojson_model = journal_marc21
    for idx, source in enumerate(sources, 1):
        click.echo(
            "({}/{}) Migrating documents in {}...".format(
                idx, len(sources), source.name
            )
        )
        data = json.load(source)
        with click.progressbar(data) as records:
            for item in records:
                click.echo(
                    'Processing series from record "{}"...'.format(
                        item["recid"]
                    )
                )
                try:
                    record_dump = CDSRecordDump(
                        item, dojson_model=dojson_model
                    )
                    try:
                        loader_class.create(record_dump, rectype)
                    except Exception as e:
                        db.session.rollback()
                        raise e

                    migrated_logger.warning(
                        "#RECID {0}: OK".format(item["recid"])
                    )
                except IlsValidationError as e:
                    records_logger.error(
                        "@RECID: {0} FATAL: {1}".format(
                            item["recid"],
                            str(e.original_exception.message),
                        )
                    )
                except Exception as e:
                    records_logger.error(
                        "@RECID: {0} ERROR: {1}".format(item["recid"], str(e))
                    )


def import_serial_from_file(sources, rectype):
    """Load serial records from file."""
    model, provider = model_provider_by_rectype(rectype)
    for idx, source in enumerate(sources, 1):
        click.echo(
            "({}/{}) Migrating documents in {}...".format(
                idx, len(sources), source.name
            )
        )
        with click.progressbar(json.load(source).items()) as bar:
            records = []
            for key, json_record in bar:
                if "legacy_recid" in json_record:
                    click.echo(
                        'Importing serial "{0}({1})"...'.format(
                            json_record["legacy_recid"], rectype
                        )
                    )
                else:
                    click.echo(
                        'Importing parent "{0}({1})"...'.format(
                            json_record["title"], rectype
                        )
                    )
                    has_children = json_record.get("_migration", {}).get(
                        "children", []
                    )
                    if has_children:
                        record = import_record(json_record, model, provider)
                        records.append(record)
