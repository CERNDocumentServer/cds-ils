# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator."""

import json

import click

from cds_ils.migrator.api import import_record
from cds_ils.migrator.handlers import (
    json_records_exception_handlers,
    multipart_record_exception_handler,
)
from cds_ils.migrator.series import journal_marc21, multipart_marc21, serial_marc21
from cds_ils.migrator.series.xml_series_loader import CDSSeriesDumpLoader
from cds_ils.migrator.xml_to_json_dump import CDSRecordDump


def import_series_from_dump(sources, rectype, loader_class=CDSSeriesDumpLoader):
    """Load serial records from given sources."""
    if rectype == "serial":
        dojson_model = serial_marc21
    elif rectype == "multipart":
        dojson_model = multipart_marc21
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
            for series_record in records:
                click.echo(
                    'Processing series from record "{}"...'.format(
                        series_record["recid"]
                    )
                )
                try:
                    record_dump = CDSRecordDump(
                        series_record, dojson_model=dojson_model
                    )
                    loader_class.create(
                        record_dump,
                        rectype,
                    )
                except Exception as exc:
                    handler = multipart_record_exception_handler.get(exc.__class__)
                    if handler:
                        handler(
                            exc,
                            legacy_id=series_record["recid"],
                            rectype=rectype,
                        )
                    else:
                        raise exc


def import_serial_from_file(sources, rectype):
    """Load serial records from file."""
    for idx, source in enumerate(sources, 1):
        click.echo(
            "({}/{}) Migrating serial in {}...".format(idx, len(sources), source.name)
        )
        with click.progressbar(json.load(source).items()) as bar:
            for key, json_record in bar:
                field = json_record.get("legacy_recid", json_record["title"])
                click.echo('Importing serial "{0}({1})"...'.format(field, rectype))
                has_children = json_record.get("_migration", {}).get("children", [])
                if has_children:
                    try:
                        import_record(
                            json_record,
                            legacy_id=json_record["title"],
                            rectype=rectype,
                            mint_legacy_pid=False,
                        )
                    except Exception as exc:
                        handler = json_records_exception_handlers.get(exc.__class__)
                        if handler:
                            handler(
                                exc,
                                legacy_id=json_record.get("title"),
                                rectype=rectype,
                            )
                        else:
                            raise exc
