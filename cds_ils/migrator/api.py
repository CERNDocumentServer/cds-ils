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
from celery import shared_task
from flask import current_app
from invenio_app_ils.acquisition.api import Order, OrderIdProvider, Vendor, \
    VendorIdProvider
from invenio_app_ils.circulation.api import IlsCirculationLoanIdProvider
from invenio_app_ils.document_requests.api import DocumentRequest, \
    DocumentRequestIdProvider
from invenio_app_ils.documents.api import Document, DocumentIdProvider
from invenio_app_ils.ill.api import BorrowingRequest, \
    BorrowingRequestIdProvider, Library, LibraryIdProvider
from invenio_app_ils.errors import IlsValidationError
from invenio_app_ils.ill.api import Library, LibraryIdProvider
from invenio_app_ils.internal_locations.api import InternalLocation, \
    InternalLocationIdProvider
from invenio_app_ils.items.api import Item, ItemIdProvider
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.relations.api import MULTIPART_MONOGRAPH_RELATION
from invenio_app_ils.series.api import Series, SeriesIdProvider
from invenio_base.app import create_cli
from invenio_circulation.api import Loan
from invenio_circulation.proxies import current_circulation
from invenio_db import db
from invenio_indexer.api import RecordIndexer

from cds_ils.importer.errors import ManualImportRequired
from cds_ils.migrator.DocumentLoader import CDSDocumentDumpLoader
from cds_ils.migrator.RecordLoader import CDSRecordDumpLoader
from cds_ils.migrator.relations.api import create_parent_child_relation
from cds_ils.migrator.series.api import clean_document_json_for_multipart, \
    exclude_multipart_fields, get_multipart_by_multipart_id, \
    replace_fields_in_volume
from cds_ils.migrator.XMLRecordToJson import CDSRecordDump

migrated_logger = logging.getLogger("migrated_records")
records_logger = logging.getLogger("records_errored")


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
        series_class = current_app_ils.series_record_cls
        return series_class, SeriesIdProvider
    elif rectype == "document":
        document_class = current_app_ils.document_record_cls
        return document_class, DocumentIdProvider
    elif rectype == "internal_location":
        internal_location_class = current_app_ils.internal_location_record_cls
        return internal_location_class, InternalLocationIdProvider
    elif rectype == "library":
        return Library, LibraryIdProvider
    elif rectype == "item":
        item_class = current_app_ils.item_record_cls
        return item_class, ItemIdProvider
    elif rectype == "loan":
        loan_class = current_circulation.loan_record_cls
        return loan_class, IlsCirculationLoanIdProvider
    elif rectype == "vendor":
        return Vendor, VendorIdProvider
    elif rectype == "borrowing-request":
        return BorrowingRequest, BorrowingRequestIdProvider
    elif rectype == "acq-order":
        return Order, OrderIdProvider
    elif rectype == "document-request":
        return DocumentRequest, DocumentRequestIdProvider
    raise ValueError("Unknown rectype: {}".format(rectype))


def import_multivolume(json_record):
    """Import multivolume type of multipart."""
    series_cls, series_pid_provider = model_provider_by_rectype("multipart")
    document_cls, document_pid_provider = model_provider_by_rectype("document")

    # build multipart dict - leave the legacy_recid attached
    multipart_json = clean_document_json_for_multipart(
        json_record, include_keys=["legacy_recid"]
    )

    # prepare json for each volume
    document_json_template = exclude_multipart_fields(
        json_record, exclude_keys=["legacy_recid"]
    )

    volume_list = json_record["_migration"]["volumes"]

    multipart_record = import_record(
        multipart_json, series_cls, series_pid_provider, legacy_id_key="title"
    )
    volumes_items_list = json_record["_migration"]["items"]
    volumes_identifiers_list = json_record["_migration"]["volumes_identifiers"]
    volumes_urls_list = json_record["_migration"]["volumes_urls"]

    lists_lenghts = [
        len(entry)
        for entry in [
            volumes_urls_list,
            volumes_items_list,
            volumes_identifiers_list,
        ]
    ]

    if any(lists_lenghts) > len(volume_list):
        raise ManualImportRequired(
            "Record has more additional volume information "
            "entries than the number of indicated volumes"
        )

    for volume in volume_list:
        replace_fields_in_volume(document_json_template, volume, json_record)
        document_record = import_record(
            document_json_template,
            document_cls,
            document_pid_provider,
            legacy_id_key="title",
        )
        create_parent_child_relation(
            multipart_record,
            document_record,
            MULTIPART_MONOGRAPH_RELATION,
            volume.get("volume"),
        )


def import_multipart(json_record):
    """Import multipart record."""
    multipart_record = None
    multipart_id = json_record["_migration"].get("multipart_id")
    series_cls, series_pid_provider = model_provider_by_rectype("multipart")
    document_cls, document_pid_provider = model_provider_by_rectype("document")

    multipart_json = clean_document_json_for_multipart(json_record)
    document_json = exclude_multipart_fields(json_record)
    volumes = json_record["_migration"]["volumes"]

    if multipart_id:
        multipart_record = get_multipart_by_multipart_id(multipart_id)
    # validate series record but only one volume document
    if multipart_id and multipart_record:
        raise ManualImportRequired(
            "Found existing multipart " "for record marked as single volume"
        )
    # series with record per volume shouldn't have more than one volume
    # in the list
    if len(volumes) != 1:
        raise ManualImportRequired("Matched volumes number incorrect.")

    # series with separate record per volume
    # (identified together with multipart id)
    if not multipart_record:
        multipart_record = import_record(
            multipart_json,
            series_cls,
            series_pid_provider,
            legacy_id_key="title",
        )
    document_record = import_record(
        document_json, document_cls, document_pid_provider
    )
    create_parent_child_relation(
        multipart_record,
        document_record,
        MULTIPART_MONOGRAPH_RELATION,
        volumes[0]["volume"],
    )


def import_multipart_from_file(dump_file, rectype):
    """Load parent records from file."""
    with click.progressbar(json.load(dump_file).items()) as bar:
        for key, legacy_record in bar:
            click.echo(
                'Importing parent "{0}({1})"...'.format(
                    legacy_record["legacy_recid"], rectype
                )
            )
            is_multivolume_record = legacy_record["_migration"].get(
                "multivolume_record", False
            )
            try:
                if is_multivolume_record:
                    import_multivolume(legacy_record)
                else:
                    import_multipart(legacy_record)
            except IlsValidationError as e:
                records_logger.error(
                    "@RECID: {0} FATAL: {1}".format(
                        legacy_record["legacy_recid"],
                        str(e.original_exception.message),
                    )
                )
            except Exception as e:
                records_logger.error(
                    "@RECID: {0} ERROR: {1}".format(
                        legacy_record["legacy_recid"], str(e)
                    )
                )


def import_serial_from_file(dump_file, rectype):
    """Load serial records from file."""
    model, provider = model_provider_by_rectype(rectype)
    with click.progressbar(json.load(dump_file).items()) as bar:
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
    # Index all new serial records
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
