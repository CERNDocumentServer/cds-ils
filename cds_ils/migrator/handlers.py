# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Migrator Records logging handler."""

import logging
from copy import deepcopy

import click
from invenio_app_ils.errors import (
    IlsValidationError,
    RecordRelationsError,
    VocabularyError,
)
from invenio_pidstore.errors import PIDAlreadyExists, PIDDoesNotExistError

from cds_ils.importer.errors import ManualImportRequired
from cds_ils.literature.api import get_record_by_legacy_recid
from cds_ils.migrator.errors import (
    AcqOrderError,
    DocumentMigrationError,
    DumpRevisionException,
    EItemMigrationError,
    FileMigrationError,
    ItemMigrationError,
    JSONConversionException,
    LoanMigrationError,
    LossyConversion,
    ProviderError,
    RelationMigrationError,
    SeriesMigrationError,
)
from cds_ils.migrator.utils import (
    get_legacy_pid_type_by_provider,
    model_provider_by_rectype,
)

cli_logger = logging.getLogger("migrator")
documents_logger = logging.getLogger("documents_logger")
items_logger = logging.getLogger("items_logger")


def migration_exception_handler(exc, output, key, value, rectype=None, **kwargs):
    """Migration exception handling - log to files.

    :param exc: exception
    :param output: generated output version
    :param key: MARC field ID
    :param value: MARC field value
    :return:
    """
    logger = logging.getLogger(f"{rectype}s_logger")
    cli_logger.error(
        "#RECID: #{0} - {1}  MARC FIELD: *{2}*, input value: {3}, -> {4}, ".format(
            output["legacy_recid"], exc.message, key, value, output
        )
    )
    logger.error(
        "MARC: {0}, INPUT VALUE: {1} ERROR: {2}" "".format(key, value, exc.message),
        extra=dict(legacy_id=output["legacy_recid"], status="WARNING", new_pid=None),
    )


def revision_exception_handler(exc, legacy_id=None, rectype=None, **kwargs):
    """Handle revision exceptions."""
    logger = logging.getLogger(f"{rectype}s_logger")
    click.secho("Revision problem", fg="red")
    logger.error(
        "CANNOT BUILD DUMP REVISIONS",
        extra=dict(legacy_id=legacy_id, status="ERROR", new_pid=None),
    )


def lossy_conversion_exception_handler(exc, legacy_id=None, rectype=None, **kwargs):
    """Handle lossy conversion exception."""
    logger = logging.getLogger(f"{rectype}s_logger")
    logger.error(
        "MIGRATION RULE MISSING {0}".format(exc.missing),
        extra=dict(legacy_id=legacy_id, status="ERROR", new_pid=None),
    )


def json_conversion_exception_handler(exc, legacy_id=None, rectype=None, **kwargs):
    """Handle json conversion exception."""
    logger = logging.getLogger(f"{rectype}s_logger")
    logger.error(
        "Impossible to convert to JSON {0}".format(exc),
        extra=dict(legacy_id=legacy_id, status="ERROR", new_pid=None),
    )


def ils_validation_error_handler(exc, legacy_id=None, rectype="document", **kwargs):
    """Handle validation error."""
    logger = logging.getLogger(f"{rectype}s_logger")
    logger.error(
        f"{str(exc.original_exception.message)}: "
        f"{str([error.res for error in exc.errors])}",
        extra=dict(legacy_id=legacy_id, status="ERROR", new_pid=None, **kwargs),
    )


def migration_validation_error_handler(
    exc, legacy_id=None, rectype="document", **kwargs
):
    """Handle validation error."""
    logger = logging.getLogger(f"{rectype}s_logger")
    logger.error(
        str(exc),
        extra=dict(legacy_id=legacy_id, status="ERROR", new_pid=None, **kwargs),
    )


def item_migration_exception_handler(
    exc,
    legacy_id=None,
    new_pid=None,
    document_legacy_recid=None,
    status=None,
    rectype=None,
    **kwargs,
):
    """Handle item migration exception."""
    record_logger = logging.getLogger(f"{rectype}s_logger")
    click.secho(str(exc), fg="blue")
    record_logger.warning(
        str(exc),
        extra=dict(
            legacy_id=legacy_id,
            new_pid=new_pid,
            document_legacy_recid=document_legacy_recid,
            status=status,
            **kwargs,
        ),
    )


def loan_migration_exception_handler(exc, legacy_id=None, **kwargs):
    """Handle loan migration exception."""
    click.secho(str(exc), fg="blue")
    loans_logger = logging.getLogger("loans_logger")
    loans_logger.error(
        str(exc),
        extra=dict(legacy_id=legacy_id, new_pid=None, status="ERROR", **kwargs),
    )


def pid_already_exists_handler(
    exc, legacy_id=None, barcode=None, rectype=None, **kwargs
):
    """Handle pid already exists exception."""
    model, provider = model_provider_by_rectype(rectype)
    legacy_pid_type = get_legacy_pid_type_by_provider(provider)
    record = get_record_by_legacy_recid(model, legacy_pid_type, legacy_id)

    message = "Record {0} already exists with pid {1}".format(
        legacy_id or barcode, record.pid
    )
    click.secho(message, fg="blue")
    raise exc


def eitem_migration_exception_handler(exc, document_pid=None, *kwargs):
    """Handle Eitem migration exception."""
    eitems_logger = logging.getLogger("eitems_logger")
    click.secho(str(exc), fg="red")
    eitems_logger.error(
        str(exc), extra=dict(document_pid=document_pid, new_pid=None, status="ERROR")
    )


def vocabulary_exception_handler(
    exc,
    legacy_id=None,
    new_pid=None,
    document_legacy_recid=None,
    status=None,
    rectype=None,
    **kwargs,
):
    """Handle vocabulary exception."""
    record_logger = logging.getLogger("vocabularies_logger")
    click.secho(str(exc), fg="blue")
    record_logger.warning(
        str(exc),
        extra=dict(
            legacy_id=legacy_id,
            new_pid=new_pid,
            document_legacy_recid=document_legacy_recid,
            status=status,
            **kwargs,
        ),
    )


def relation_exception_handler(exc, **kwargs):
    """Handle relation already exists exception."""
    relations_logger = logging.getLogger("relations_logger")
    relations_logger.warning(
        str(exc),
        extra=dict(
            legacy_id=kwargs.get("legacy_id"),
            status="ERROR",
            new_pid=kwargs.get("new_pid"),
        ),
    )


def related_record_not_found(exc, raise_exceptions=False, **kwargs):
    """Handle not found exceptions."""
    relations_logger = logging.getLogger("relations_logger")
    if isinstance(exc, PIDDoesNotExistError):
        message = f"Record legacy " f"id {exc.pid_value}({exc.pid_type}) not found."
    else:
        message = str(exc)
    relations_logger.error(
        message,
        extra=dict(
            legacy_id=kwargs.get("legacy_id"),
            status="ERROR",
            new_pid=kwargs.get("new_pid"),
        ),
    )

    if raise_exceptions:
        raise exc


def default_error_handler(
    exc, legacy_id=None, rectype="document", raise_exceptions=False, **kwargs
):
    """Handle any error."""
    logger = logging.getLogger(f"{rectype}s_logger")
    logger.error(
        str(exc),
        extra=dict(legacy_id=legacy_id, status="ERROR", new_pid=None, **kwargs),
    )
    if raise_exceptions:
        raise exc


json_records_exception_handlers = {
    IlsValidationError: ils_validation_error_handler,
    DocumentMigrationError: item_migration_exception_handler,
    ItemMigrationError: item_migration_exception_handler,
    LoanMigrationError: loan_migration_exception_handler,
    # raised if not CDS_ILS_MIGRATION_ALLOW_UPDATES
    PIDAlreadyExists: pid_already_exists_handler,
}

xml_record_exception_handlers = {
    IlsValidationError: ils_validation_error_handler,
    JSONConversionException: json_conversion_exception_handler,
    LossyConversion: lossy_conversion_exception_handler,
    DumpRevisionException: revision_exception_handler,
    # raised if not CDS_ILS_MIGRATION_ALLOW_UPDATES
    PIDAlreadyExists: pid_already_exists_handler,
    RecordRelationsError: relation_exception_handler,
    VocabularyError: vocabulary_exception_handler,
}

multipart_record_exception_handler = deepcopy(xml_record_exception_handlers)

multipart_record_exception_handler.update(
    {
        RecordRelationsError: relation_exception_handler,
        ManualImportRequired: migration_validation_error_handler,
        SeriesMigrationError: migration_validation_error_handler,
    }
)

acquisition_order_exception_handler = deepcopy(json_records_exception_handlers)

acquisition_order_exception_handler.update(
    {
        AcqOrderError: migration_validation_error_handler,
        ProviderError: migration_validation_error_handler,
    }
)

eitems_exception_handlers = {
    IlsValidationError: ils_validation_error_handler,
    EItemMigrationError: eitem_migration_exception_handler,
    AssertionError: eitem_migration_exception_handler,
    FileMigrationError: eitem_migration_exception_handler,
}

relation_exception_handlers = {
    RecordRelationsError: relation_exception_handler,
    RelationMigrationError: related_record_not_found,
    PIDDoesNotExistError: related_record_not_found,
    DocumentMigrationError: relation_exception_handler,
}
