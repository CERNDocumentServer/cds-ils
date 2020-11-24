# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Migrator Records MARCXML to JSON dump."""
import logging

import arrow
from cds_dojson.marc21.utils import create_record
from flask import current_app

from cds_ils.importer import marc21
from cds_ils.importer.errors import ManualImportRequired, \
    MissingRequiredField, UnexpectedValue
from cds_ils.migrator.errors import LossyConversion
from cds_ils.migrator.handlers import migration_exception_handler

cli_logger = logging.getLogger("migrator")


class CDSRecordDump(object):
    """CDS record dump class."""

    def __init__(
        self,
        data,
        source_type="marcxml",
        latest_only=True,
        dojson_model=marc21,
    ):
        """Initialize."""
        self.data = data
        self.source_type = source_type
        self.latest_only = latest_only
        self.dojson_model = dojson_model
        self.revisions = None

    @property
    def created(self):
        """Get creation date."""
        return self.revisions[0][0]

    def prepare_revisions(self):
        """Prepare data."""
        # Prepare revisions
        self.revisions = []

        it = (
            [self.data["record"][0]]
            if self.latest_only
            else self.data["record"]
        )

        for i in it:
            self.revisions.append(self._prepare_revision(i))

    def prepare_files(self):
        """Get files from data dump."""
        # Prepare files
        files = {}
        for f in self.data["files"]:
            k = f["full_name"]
            if k not in files:
                files[k] = []
            files[k].append(f)

        # Sort versions
        for k in files.keys():
            files[k].sort(key=lambda x: x["version"])

    def _prepare_revision(self, data):
        dt = arrow.get(data["modification_datetime"]).datetime

        exception_handlers = {
            UnexpectedValue: migration_exception_handler,
            MissingRequiredField: migration_exception_handler,
            ManualImportRequired: migration_exception_handler,
        }

        if self.source_type == "marcxml":
            marc_record = create_record(data["marcxml"])
            try:
                val = self.dojson_model.do(
                    marc_record, exception_handlers=exception_handlers
                )
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
                raise e
            except Exception as e:
                current_app.logger.error(
                    "Impossible to convert to JSON {0} - {1}".format(
                        e, marc_record
                    )
                )
                raise e
        else:
            val = data["json"]

            # Calculate the _access key
            return dt, val
