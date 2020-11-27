# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2020 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Migrator Records exceptions."""

from dojson.errors import DoJSONException


class LossyConversion(DoJSONException):
    """Data lost during migration."""

    def __init__(self, *args, **kwargs):
        """Exception custom initialisation."""
        self.missing = kwargs.pop("missing", None)
        self.message = "Lossy conversion: {0}".format(self.missing or "")
        super().__init__(*args, **kwargs)


class RecordNotDeletable(DoJSONException):
    """Record is not marked as deletable."""

    def __init__(self, *args, **kwargs):
        """Exception custom initialisation."""
        self.message = "Record is not marked as deletable"
        super().__init__(*args, **kwargs)


class ProviderNotAllowedDeletion(DoJSONException):
    """Provider is not allowed to delete records."""

    def __init__(self, *args, **kwargs):
        """Exception custom initialisation."""
        self.provider = kwargs.pop("provider", None)
        self.message = "This provider {0} is not allowed to delete records"\
            .format(self.provider)
        super().__init__(*args, **kwargs)


class CDSImporterException(DoJSONException):
    """CDSDoJSONException class."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        self.subfield = kwargs.get("subfield", None)
        message = kwargs.get("message", None)
        if message:
            self.message = self.message + message

        super(CDSImporterException, self).__init__(*args)


class UnexpectedValue(CDSImporterException):
    """The corresponding value is unexpected."""

    message = "[UNEXPECTED INPUT VALUE]"


class MissingRequiredField(CDSImporterException):
    """The corresponding value is required."""

    message = "[MISSING REQUIRED FIELD]"


class ManualImportRequired(CDSImporterException):
    """The corresponding field should be manually migrated."""

    message = "[MANUAL MIGRATION REQUIRED]"


class DocumentImportError(CDSImporterException):
    """Document import exception."""

    message = "[DOCUMENT IMPORT ERROR]"


class SeriesImportError(CDSImporterException):
    """Document import exception."""

    message = "[SERIES IMPORT ERROR]"
