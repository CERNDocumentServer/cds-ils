# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer exception handlers module."""
from invenio_app_ils.errors import (
    IlsValidationError,
    RecordHasReferencesError,
    VocabularyError,
)
from invenio_pidstore.errors import PIDDeletedError

from cds_ils.importer.errors import (
    DocumentHasReferencesError,
    InvalidProvider,
    LossyConversion,
    ManualImportRequired,
    MissingRequiredField,
    ProviderNotAllowedDeletion,
    RecordModelMissing,
    RecordNotDeletable,
    SeriesImportError,
    SimilarityMatchUnavailable,
    UnexpectedValue,
    UnknownProvider,
)
from cds_ils.importer.models import ImportRecordLog


def get_importer_handler(exc, log):
    """Get correct exception handler."""
    if exc.__class__ in importer_exception_handlers:
        handler = importer_exception_handlers[exc.__class__]
        if handler is not None:
            return handler
    else:
        log.set_failed(exc)
        raise exc


def default_xml_exception_handler(exc, output, key, *args, **kwargs):
    """Default handler for xml to json conversion exceptions."""
    exc.message = exc.description = f"{exc.message} in <{key}{exc.subfield}> "
    raise exc


def default_invenio_exception_handler(
    exc, log_id, record_recid, json_data=None, *args, **kwargs
):
    """Handle invenio exception."""
    ImportRecordLog.create_failure(
        log_id,
        record_recid,
        f"{exc.__class__.__name__} {str(exc)}",
        report={"raw_json": json_data},
    )


def pid_deleted_exception_handler(
    exc, log_id, record_recid, json_data=None, *args, **kwargs
):
    """Handle invenio exception."""
    ImportRecordLog.create_failure(
        log_id,
        record_recid,
        f"{exc.__class__.__name__} {exc.pid_type}: {exc.pid_value}",
        report={"raw_json": json_data},
    )


def ils_validation_exception_handler(
    exc, log_id, record_recid, json_data=None, *args, **kwargs
):
    """Handle ILS exception."""
    ImportRecordLog.create_failure(
        log_id,
        record_recid,
        str(exc.original_exception.message),
        report={"raw_json": json_data},
    )


def importer_exception_handler(
    exc, log_id, record_recid, json_data=None, *args, **kwargs
):
    """Handle importer exception."""
    output_pid = getattr(exc, "record_id", None)
    report = {"raw_json": json_data, "output_pid": output_pid}
    ImportRecordLog.create_failure(
        log_id, record_recid, str(exc.description), report=report
    )


def python_exception_handler(exc, output, key, *args, **kwargs):
    """Default handler for xml to json conversion exceptions."""
    exception = UnexpectedValue()
    exception.message = exception.description = f"{str(exc)} in <{key}> "
    raise exception


xml_import_handlers = {
    UnexpectedValue: default_xml_exception_handler,
    MissingRequiredField: default_xml_exception_handler,
    ManualImportRequired: default_xml_exception_handler,
    AttributeError: python_exception_handler,
}

importer_exception_handlers = {
    PIDDeletedError: pid_deleted_exception_handler,
    RecordNotDeletable: importer_exception_handler,
    ProviderNotAllowedDeletion: importer_exception_handler,
    SeriesImportError: importer_exception_handler,
    RecordHasReferencesError: importer_exception_handler,
    DocumentHasReferencesError: importer_exception_handler,
    UnknownProvider: importer_exception_handler,
    VocabularyError: importer_exception_handler,
    InvalidProvider: importer_exception_handler,
    SimilarityMatchUnavailable: importer_exception_handler,
    LossyConversion: importer_exception_handler,
    UnexpectedValue: importer_exception_handler,
    RecordModelMissing: importer_exception_handler,
    MissingRequiredField: importer_exception_handler,
    IlsValidationError: ils_validation_exception_handler,
}
