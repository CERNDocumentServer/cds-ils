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
        super().__init__(*args)


class DumpRevisionException(Exception):
    """Exception for dump revision."""


class JSONConversionException(Exception):
    """JSON Conversion Exception in migration."""


class CdsIlsMigrationException(Exception):
    """Base exception for CDS-ILS migration errors."""


class DocumentMigrationError(CdsIlsMigrationException):
    """Raised for multipart migration errors."""


class SeriesMigrationError(CdsIlsMigrationException):
    """Raised for multipart migration errors."""


class MultipartMigrationError(CdsIlsMigrationException):
    """Raised for multipart migration errors."""


class UserMigrationError(CdsIlsMigrationException):
    """Raised for user migration errors."""


class SerialMigrationError(CdsIlsMigrationException):
    """Raised for serial migration errors."""


class ItemMigrationError(CdsIlsMigrationException):
    """Raised for item migration errors."""


class LoanMigrationError(CdsIlsMigrationException):
    """Raised for loan migration errors."""


class EItemMigrationError(CdsIlsMigrationException):
    """Raised for EItem migration errors."""


class FileMigrationError(CdsIlsMigrationException):
    """Raised for File migration errors."""


class BorrowingRequestError(CdsIlsMigrationException):
    """Raised for borrowing request migration errors."""


class AcqOrderError(CdsIlsMigrationException):
    """Raised for acquisition order migration errors."""


class ProviderError(CdsIlsMigrationException):
    """Raised for provider migration errors."""


class RelationMigrationError(CdsIlsMigrationException):
    """Raised for exceptions when migrating relations."""
