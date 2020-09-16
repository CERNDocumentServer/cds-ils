# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator API."""

import json
import logging
from contextlib import contextmanager

import click
from flask import current_app
from invenio_app_ils.circulation.api import IlsCirculationLoanIdProvider
from invenio_app_ils.documents.api import Document, DocumentIdProvider
from invenio_app_ils.ill.api import Library, LibraryIdProvider
from invenio_app_ils.internal_locations.api import InternalLocation, \
    InternalLocationIdProvider
from invenio_app_ils.items.api import Item, ItemIdProvider
from invenio_app_ils.series.api import Series, SeriesIdProvider
from invenio_base.app import create_cli
from invenio_circulation.api import Loan
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from cds_ils.migrator.records import CDSRecordDumpLoader

migrated_logger = logging.getLogger("migrated_documents")


@contextmanager
def commit():
    """Commit transaction or rollback in case of an exception."""
    try:
        yield
        db.session.commit()
    except Exception:
        print("Rolling back changes...")
        db.session.rollback()
        raise


def reindex_pidtype(pid_type):
    """Reindex records with the specified pid_type."""
    click.echo('Indexing pid type "{}"...'.format(pid_type))
    cli = create_cli()
    runner = current_app.test_cli_runner()
    runner.invoke(
        cli,
        "index reindex --pid-type {} --yes-i-know".format(pid_type),
        catch_exceptions=False,
    )
    runner.invoke(cli, "index run", catch_exceptions=False)
    click.echo("Indexing completed!")


def bulk_index_records(records):
    """Bulk index a list of records."""
    indexer = RecordIndexer()

    click.echo("Bulk indexing {} records...".format(len(records)))
    indexer.bulk_index([str(r.id) for r in records])
    indexer.process_bulk_queue()
    click.echo("Indexing completed!")


def model_provider_by_rectype(rectype):
    """Return the correct model and PID provider based on the rectype."""
    if rectype in ("serial", "multipart"):
        return Series, SeriesIdProvider
    elif rectype == "document":
        return Document, DocumentIdProvider
    elif rectype == "internal_location":
        return InternalLocation, InternalLocationIdProvider
    elif rectype == "library":
        return Library, LibraryIdProvider
    elif rectype == "item":
        return Item, ItemIdProvider
    elif rectype == "loan":
        return Loan, IlsCirculationLoanIdProvider
    else:
        raise ValueError("Unknown rectype: {}".format(rectype))


def import_parents_from_file(dump_file, rectype, include):
    """Load parent records from file."""
    model, provider = model_provider_by_rectype(rectype)
    include_keys = None if include is None else include.split(",")
    with click.progressbar(json.load(dump_file).items()) as bar:
        records = []
        for key, parent in bar:
            if "legacy_recid" in parent:
                click.echo(
                    'Importing parent "{0}({1})"...'.format(
                        parent["legacy_recid"], rectype
                    )
                )
            else:
                click.echo(
                    'Importing parent "{0}({1})"...'.format(
                        parent["title"], rectype
                    )
                )
            if include_keys is None or key in include_keys:
                has_children = parent.get("_migration", {}).get("children", [])
                has_volumes = parent.get("_migration", {}).get("volumes", [])
                if rectype == "serial" and has_children:
                    record = import_record(parent, model, provider)
                    records.append(record)
                elif rectype == "multipart" and has_volumes:
                    record = import_record(parent, model, provider)
                    records.append(record)
    # Index all new parent records
    bulk_index_records(records)


def import_record(dump, model, pid_provider, legacy_id_key="legacy_recid"):
    """Import record in database."""
    record = CDSRecordDumpLoader.create(
        dump, model, pid_provider, legacy_id_key
    )
    return record


