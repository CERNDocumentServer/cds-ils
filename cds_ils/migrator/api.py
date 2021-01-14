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

import click
from celery import shared_task
from invenio_app_ils.errors import IlsValidationError
from invenio_db import db

from cds_ils.migrator.json_record_loader import CDSRecordDumpLoader
from cds_ils.migrator.xml_document_loader import CDSDocumentDumpLoader
from cds_ils.migrator.xml_to_json_dump import CDSRecordDump

migrated_logger = logging.getLogger("migrated_records")
records_logger = logging.getLogger("records_errored")


def import_documents_from_dump(sources, source_type, eager, include):
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
            for item in records:
                click.echo('Processing document "{}"...'.format(item["recid"]))
                if include is None or str(item["recid"]) in include:
                    try:
                        import_document_from_dump(
                            item, source_type, eager=eager
                        )

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
                            "@RECID: {0} ERROR: {1}".format(
                                item["recid"], str(e)
                            )
                        )


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
    record_dump = CDSRecordDump(
        data,
        source_type=source_type,
    )
    try:
        CDSDocumentDumpLoader.create(record_dump)
    except Exception as e:
        db.session.rollback()
        raise e
