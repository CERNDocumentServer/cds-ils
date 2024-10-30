# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2020 CERN.
#
# cds-ils is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Exceptions."""

from dojson.errors import DoJSONException
from invenio_app_ils.errors import RecordHasReferencesError


class LossyConversion(DoJSONException):
    """Data lost during migration."""

    def __init__(self, *args, **kwargs):
        """Exception custom initialisation."""
        self.missing = kwargs.pop("missing", None)
        self.message = self.description = "Lossy conversion: {0}".format(
            self.missing or ""
        )
        super().__init__(*args, **kwargs)


class RecordNotDeletable(DoJSONException):
    """Record is not marked as deletable."""

    def __init__(self, *args, **kwargs):
        """Exception custom initialisation."""
        self.message = self.description = "Record is not marked as deletable"
        super().__init__(*args, **kwargs)


class ProviderNotAllowedDeletion(DoJSONException):
    """Provider is not allowed to delete records."""

    def __init__(self, *args, **kwargs):
        """Exception custom initialisation."""
        self.provider = kwargs.pop("provider", None)
        self.message = self.description = (
            "This provider {0} is not allowed to delete records".format(self.provider)
        )
        super().__init__(*args, **kwargs)


class CDSImporterException(DoJSONException):
    """CDSDoJSONException class."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        self.subfield = kwargs.get("subfield", "")
        message = kwargs.get("message", None)
        if message:
            self.message = message

        # because of ILSRestException class attributes
        self.description = self.message

        super(CDSImporterException, self).__init__(*args)


class DocumentHasReferencesError(RecordHasReferencesError):
    """DocumentHasReferencesError class."""

    def __init__(self, document, ref_type, refs):
        """Constructor."""
        ref_ids = sorted([res["pid"] for res in refs.scan()])
        super().__init__(
            record_type="Document",
            record_id=document["pid"],
            ref_type=ref_type,
            ref_ids=ref_ids,
        )


class RecordModelMissing(CDSImporterException):
    """Missing record model exception."""

    message = "[Record did not match any available model]"


class UnrecognisedImportMediaType(CDSImporterException):
    """Unrecognised record media type exception."""

    message = "Record media type is not recognised."


class UnexpectedValue(CDSImporterException):
    """The corresponding value is unexpected."""

    message = "[UNEXPECTED INPUT VALUE]"


class MissingRequiredField(CDSImporterException):
    """The corresponding value is required."""

    message = "[MISSING REQUIRED FIELD]"


class ManualImportRequired(CDSImporterException):
    """The corresponding field should be manually migrated."""

    message = "[MANUAL IMPORT REQUIRED]"


class DocumentImportError(CDSImporterException):
    """Document import exception."""

    message = "[DOCUMENT IMPORT ERROR]"


class SeriesImportError(CDSImporterException):
    """Document import exception."""

    message = "[SERIES IMPORT ERROR]"


class UnknownProvider(CDSImporterException):
    """Unknown provider exception."""

    message = "Unknown record provider."


class InvalidProvider(CDSImporterException):
    """Invalid provider exception."""

    message = "Invalid record provider."


class SimilarityMatchUnavailable(CDSImporterException):
    """Similarity match unavailable exception."""

    message = (
        "Title similarity matching cannot be performed for "
        "this record. Please import it manually."
    )
