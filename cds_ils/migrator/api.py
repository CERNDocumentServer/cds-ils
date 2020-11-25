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
from warnings import warn

import click
from celery import shared_task
from elasticsearch_dsl import Q
from flask import current_app
from invenio_app_ils.acquisition.api import Order, OrderIdProvider, Vendor, \
    VendorIdProvider
from invenio_app_ils.circulation.api import IlsCirculationLoanIdProvider
from invenio_app_ils.document_requests.api import DocumentRequest, \
    DocumentRequestIdProvider
from invenio_app_ils.documents.api import Document, DocumentIdProvider
from invenio_app_ils.ill.api import BorrowingRequest, \
    BorrowingRequestIdProvider, Library, LibraryIdProvider
from invenio_app_ils.internal_locations.api import InternalLocation, \
    InternalLocationIdProvider
from invenio_app_ils.items.api import Item, ItemIdProvider
from invenio_app_ils.series.api import Series, SeriesIdProvider
from invenio_app_ils.series.search import SeriesSearch
from invenio_base.app import create_cli
from invenio_circulation.api import Loan
from invenio_db import db
from invenio_indexer.api import RecordIndexer

from cds_ils.migrator.DocumentLoader import CDSDocumentDumpLoader
from cds_ils.migrator.RecordLoader import CDSRecordDumpLoader
from cds_ils.migrator.XMLRecordToJson import CDSRecordDump

migrated_logger = logging.getLogger("migrated_records")


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
        catch_exceptions=True,
    )
    runner.invoke(cli, "index run", catch_exceptions=True)
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
    elif rectype == "vendor":
        return Vendor, VendorIdProvider
    elif rectype == "borrowing-request":
        return BorrowingRequest, BorrowingRequestIdProvider
    elif rectype == "acq-order":
        return Order, OrderIdProvider
    elif rectype == "document-request":
        return DocumentRequest, DocumentRequestIdProvider
    raise ValueError("Unknown rectype: {}".format(rectype))


def import_parents_from_file(dump_file, rectype, include):
    """Load parent records from file."""
    model, provider = model_provider_by_rectype(rectype)
    include_keys = None if include is None else include.split(",")
    with click.progressbar(json.load(dump_file).items()) as bar:
        records = []
        unindexed_series = dict()
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
                    existing_parent = None
                    multipart_id = parent["_migration"].get("multipart_id")
                    if multipart_id:
                        if multipart_id in unindexed_series:
                            existing_parent = unindexed_series[multipart_id]
                        else:
                            search = SeriesSearch().query(
                                "bool",
                                filter=[
                                    Q("term",
                                      _migration__serial_id=multipart_id),
                                ],
                            )
                            results = search.execute()
                            hits_total = results.hits.total.value
                            if hits_total > 0:
                                existing_parent = results.hits[0]
                            else:
                                unindexed_series[multipart_id] = parent
                    if not existing_parent:
                        record = import_record(parent, model, provider)
                        if record:
                            records.append(record)
                    else:
                        # TODO ensure the parent record is actually the same
                        warn("Multipart parent record already exists,"
                             "ignoring.")
    # Index all new parent records
    bulk_index_records(records)


def import_record(dump, model, pid_provider, legacy_id_key="legacy_recid"):
    """Import record in database."""
    record = CDSRecordDumpLoader.create(
        dump, model, pid_provider, legacy_id_key
    )
    return record


def import_document_from_dump(data, source_type=None, eager=False):
    """Import record from dump."""
    source_type = source_type or "marcxml"
    assert source_type in ["marcxml"]

    if eager:
        return process_document_dump(data, source_type)
    else:
        process_document_dump.delay(data, source_type)


@shared_task()
def process_document_dump(data, source_type=None):
    """Migrate a document from a migration dump.

    :param data: Dictionary for representing a single record and files.
    """
    recorddump = CDSRecordDump(
        data,
        source_type=source_type,
    )
    try:
        CDSDocumentDumpLoader.create(recorddump)
    except Exception as e:
        db.session.rollback()
        raise e
