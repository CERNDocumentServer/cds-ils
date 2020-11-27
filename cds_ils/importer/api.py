# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer API module."""
import logging

from celery import shared_task
from flask import current_app
from invenio_app_ils.errors import IlsValidationError
from invenio_db import db

from cds_ils.importer.errors import LossyConversion, \
    ProviderNotAllowedDeletion, RecordNotDeletable
from cds_ils.importer.models import ImporterTaskEntry, ImporterTaskLog
from cds_ils.importer.parse_xml import get_records_list
from cds_ils.importer.XMLRecordLoader import XMLRecordDumpLoader
from cds_ils.importer.XMLRecordToJson import XMLRecordToJson

records_logger = logging.getLogger("records_errored")


@shared_task()
def process_dump(data, provider, mode, source_type):
    """Process record dump."""
    recorddump = XMLRecordToJson(
        data,
        source_type=source_type,
    )
    try:
        report = XMLRecordDumpLoader.process(recorddump, provider, mode)
        db.session.commit()
        return report
    except Exception as e:
        db.session.rollback()
        raise e


def import_record(data, provider, mode, source_type=None, eager=False):
    """Import record from dump."""
    source_type = source_type or "marcxml"
    assert source_type in ["marcxml"]

    if provider not in current_app.config[
        "CDS_ILS_IMPORTER_PROVIDERS_ALLOWED_TO_DELETE_RECORDS"
    ] and mode == 'delete':
        raise ProviderNotAllowedDeletion(provider=provider)
    if eager:
        return process_dump(data, provider, mode, source_type=source_type)
    else:
        process_dump.delay(data, provider, mode, source_type=source_type)


def import_from_xml(log_id, source_path, source_type, provider, mode):
    """Load a single xml file."""
    log = ImporterTaskLog.query.filter_by(id=log_id).first()
    entry_data = None
    try:
        with open(source_path) as source:
            records_list = list(get_records_list(source))

            # update the entries count now that we know it
            log.entries_count = len(records_list)
            db.session.commit()

            for i, record in enumerate(records_list):
                entry_data = dict(
                    import_id=log.id,
                    entry_index=i,
                )
                try:
                    report = import_record(record, provider, mode,
                                           source_type=source_type,
                                           eager=True)
                except (LossyConversion, RecordNotDeletable,
                        ProviderNotAllowedDeletion) as e:
                    ImporterTaskEntry.create_failure(entry_data, e)
                    continue
                except IlsValidationError as e:
                    records_logger.error(
                        "@FILE TASK: {0} FATAL: {1}".format(
                            log_id,
                            str(e.original_exception.message),
                        )
                    )
                    ImporterTaskEntry.create_failure(entry_data, e)
                    continue

                ImporterTaskEntry.create_success(entry_data, report)
    except Exception as e:
        records_logger.error(
            "@FILE TASK: {0} ERROR: {1}".format(log_id, str(e))
        )
        if entry_data:
            ImporterTaskEntry.create_failure(entry_data, e)
        log.set_failed(e)
        raise e

    log.set_succeeded()
