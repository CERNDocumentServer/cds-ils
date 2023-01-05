# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator API."""

import csv
import json

import click
from celery import shared_task
from invenio_db import db

from cds_ils.migrator.documents.xml_document_loader import CDSDocumentDumpLoader
from cds_ils.migrator.handlers import (
    default_error_handler,
    xml_record_exception_handlers,
)
from cds_ils.migrator.json_record_loader import CDSRecordDumpLoader
from cds_ils.migrator.xml_to_json_dump import CDSRecordDump


def import_documents_from_dump(
    sources, source_type, eager, include, rectype="document", raise_exceptions=False
):
    """Load records."""
    include = include if include is None else include.split(",")

    for idx, source in enumerate(sources, 1):
        click.echo(
            "({}/{}) Migrating documents in {}...".format(
                idx, len(sources), source.name
            )
        )
        data = json.load(source)
        with click.progressbar(data) as records:
            for dump_record in records:
                click.echo('Processing document "{}"...'.format(dump_record["recid"]))
                if include is None or str(dump_record["recid"]) in include:
                    try:
                        import_document_from_dump(dump_record, source_type, eager=eager)
                    except Exception as exc:
                        handler = xml_record_exception_handlers.get(exc.__class__)
                        if handler:
                            handler(
                                exc, legacy_id=dump_record["recid"], rectype=rectype
                            )
                        else:
                            default_error_handler(
                                exc,
                                rectype=rectype,
                                raise_exceptions=raise_exceptions,
                                legacy_id=dump_record["recid"],
                            )


def import_record(dump, rectype, legacy_id, mint_legacy_pid=True, log_extra={}):
    """Import record in database."""
    record = CDSRecordDumpLoader.create(
        dump, rectype, legacy_id, mint_legacy_pid=mint_legacy_pid, log_extra=log_extra
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
    record_dump = CDSRecordDump(
        data,
        source_type=source_type,
    )
    try:
        CDSDocumentDumpLoader.create(record_dump)
    except Exception as e:
        db.session.rollback()
        raise e


def document_migration_report(
    log_file, recid_list_file, output_filepath="/tmp/documents_report.csv"
):
    """Generate document migration report."""
    # columns: 0          1     2       3          4        5
    #         datetime    sec   recid   new_pid    status   message
    recid_list = json.load(recid_list_file)
    csv_iter = csv.reader(log_file)

    with open(output_filepath, "w") as csvoutput:
        writer = csv.writer(csvoutput, lineterminator="\n")
        for row in csv_iter:
            recid, status, message = (
                int(row[2].strip()),
                row[4].strip(),
                row[5].strip(),
            )
            if recid not in recid_list:
                migration_status = "EXTRA"
            else:
                if status == "SUCCESS":
                    recid_list.remove(recid)
                    migration_status = "OK"
                elif status == "WARNING":
                    recid_list.remove(recid)
                    migration_status = "PARTIAL"
                else:
                    migration_status = "NOT_MIGRATED"
            row[6] = migration_status
            writer.writerow(row)

    with open("/tmp/documents_errored.json", "w") as outfile:
        json.dump(recid_list, outfile)


def items_migration_report(
    log_file, recid_list_file, output_filepath="/tmp/items_report.csv"
):
    """Generate item migration report."""
    # 2           3        4                       5      6        7
    # barcode   new_pid    document_legacy_recid  status  message
    recid_list = json.load(recid_list_file)
    csv_iter = csv.reader(log_file)
    documents_with_migrated_items_list = []

    with open(output_filepath, "w") as csvoutput:
        writer = csv.writer(csvoutput, lineterminator="\n")
        for row in csv_iter:
            barcode, status, message = (
                row[2].strip(),
                row[5].strip(),
                row[6].strip(),
            )
            try:
                document_legacy_recid = int(row[4].strip())
            except ValueError:
                document_legacy_recid = 0

            # check if item should be migrated
            if document_legacy_recid not in recid_list:
                migration_status = "EXTRA"
            else:
                if status == "SUCCESS":
                    documents_with_migrated_items_list.append(document_legacy_recid)
                    migration_status = "OK"
                elif status == "WARNING":
                    documents_with_migrated_items_list.append(document_legacy_recid)
                    migration_status = "PARTIAL"
                else:
                    migration_status = "NOT_MIGRATED"
            row[7] = migration_status
            writer.writerow(row)

        documents_with_migrated_items_list = list(
            set(documents_with_migrated_items_list)
        )
        documents_with_missing_items = [
            doc for doc in recid_list if doc not in documents_with_migrated_items_list
        ]
        with open("/tmp/documents_with_missing_items.json", "w") as outfile:
            json.dump(documents_with_missing_items, outfile)
        with open("/tmp/documents_with_migrated_items.json", "w") as outfile:
            json.dump(documents_with_migrated_items_list, outfile)
