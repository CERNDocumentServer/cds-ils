# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Migrator Records loader."""
import datetime

from cds_dojson.marc21.fields.books.errors import ManualMigrationRequired, \
    MissingRequiredField, UnexpectedValue
from cds_dojson.marc21.utils import create_record
from flask import current_app
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record

from cds_ils.importer import marc21
from cds_ils.importer.errors import LossyConversion
from cds_ils.importer.handlers import importer_exception_handler


class XMLRecordDump(object):
    """Handle record dump from marcxml."""

    def __init__(
        self,
        data,
        source_type="marcxml",
        latest_only=False,
        pid_fetchers=None,
        dojson_model=marc21,
    ):
        """Initialize class."""
        self.resolver = Resolver(
            pid_type="recid", object_type="rec", getter=Record.get_record
        )
        self.data = data
        self.source_type = source_type
        self.latest_only = latest_only
        self.dojson_model = dojson_model
        self.revisions = None
        self.pid_fetchers = pid_fetchers or []

    def dump(self):
        """Perform record dump."""
        dt = datetime.datetime.utcnow()

        exception_handlers = {
            UnexpectedValue: importer_exception_handler,
            MissingRequiredField: importer_exception_handler,
            ManualMigrationRequired: importer_exception_handler,
        }

        marc_record = create_record(self.data)

        try:

            # MARCXML -> JSON fields translation
            val = self.dojson_model.do(
                marc_record, exception_handlers=exception_handlers
            )
            # check for missing rules
            missing = self.dojson_model.missing(marc_record)

            if missing:
                raise LossyConversion(missing=missing)
            return dt, val

        except LossyConversion as e:
            current_app.logger.error(
                "MIGRATION RULE MISSING {0} - {1}".format(
                    e.missing, marc_record
                )
            )
        except Exception as e:
            current_app.logger.error(
                "Impossible to convert to JSON {0} - {1}".format(
                    e, marc_record
                )
            )
            raise e
