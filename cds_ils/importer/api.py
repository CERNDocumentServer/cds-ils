# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer API module."""

import uuid

from flask import current_app
from invenio_db import db

from cds_ils.importer.errors import ProviderNotAllowedDeletion
from cds_ils.importer.handlers import get_importer_handler
from cds_ils.importer.models import ImporterMode, ImporterTaskStatus, ImportRecordLog
from cds_ils.importer.parse_xml import get_record_recid_from_xml, get_records_list
from cds_ils.importer.vocabularies_validator import validator as vocabulary_validator
from cds_ils.importer.XMLRecordLoader import XMLRecordDumpLoader
from cds_ils.importer.XMLRecordToJson import XMLRecordToJson


def create_json(data, source_type, ignore_missing_rules=False):
    """Process record dump."""
    record_dump = XMLRecordToJson(
        data, source_type=source_type, ignore_missing=ignore_missing_rules
    )
    return XMLRecordDumpLoader.create_json(record_dump)


def import_from_json(json_data, is_deletable, provider, mode):
    """Import from Json."""
    try:
        report = XMLRecordDumpLoader.import_from_json(
            json_data, is_deletable, provider, mode
        )
        db.session.commit()
        return report
    except Exception as e:
        db.session.rollback()
        raise e


def validate_import(provider, mode, source_type):
    """Validate import."""
    source_type = source_type or "marcxml"
    assert source_type in ["marcxml"]

    # check if the record is in delete mode
    if (
        provider
        not in current_app.config[
            "CDS_ILS_IMPORTER_PROVIDERS_ALLOWED_TO_DELETE_RECORDS"
        ]
        and mode == ImporterMode.DELETE.value
    ):
        raise ProviderNotAllowedDeletion(provider=provider)


def import_from_xml(
    log,
    source_path,
    source_type,
    provider,
    mode,
    ignore_missing_rules=False,
    eager=False,
):
    """Load a single xml file."""
    try:
        # reset vocabularies validator cache
        vocabulary_validator.reset()
        validate_import(provider, mode, source_type)

        with open(source_path, "r") as source:
            records_list = list(get_records_list(source))

            # update the entries count now that we know it
            log.set_entries_count(records_list)
            for record in records_list:
                if log.status == ImporterTaskStatus.CANCELLED:
                    break

                record_recid = get_record_recid_from_xml(record)

                # step 1: translate XML
                try:
                    json_data, is_deletable = create_json(
                        record, source_type, ignore_missing_rules=ignore_missing_rules
                    )
                except Exception as exc:
                    handler = get_importer_handler(exc, log)
                    handler(exc, log.id, record_recid)
                    continue

                # step 2: import json
                try:
                    report = import_from_json(json_data, is_deletable, provider, mode)
                    ImportRecordLog.create_success(log.id, record_recid, report)
                except Exception as exc:
                    handler = get_importer_handler(exc, log)
                    handler(exc, log.id, record_recid, json_data=json_data)
                    continue

    except Exception as exc:
        handler = get_importer_handler(exc, log)
        handler(exc, log.id, None)
        log.set_failed(exc)

    log.finalize()


def allowed_files(filename):
    """Checks the extension of the files."""
    allowed_extensions = current_app.config["CDS_ILS_IMPORTER_FILE_EXTENSIONS_ALLOWED"]
    return filename.lower().endswith(tuple(allowed_extensions))


def rename_file(filename):
    """Renames filename with an unique name."""
    unique_filename = uuid.uuid4().hex
    ext = filename.rsplit(".", 1)[1]
    return unique_filename + "." + ext
