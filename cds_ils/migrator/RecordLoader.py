# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Migrator Records loader."""

import logging
import uuid

import click
from invenio_app_ils.errors import IlsValidationError
from invenio_db import db

cli_logger = logging.getLogger("migrator")


class CDSRecordDumpLoader(object):
    """Migrate a CDS records."""

    @classmethod
    def create(cls, dump, model, pid_provider, legacy_id_key="legacy_recid"):
        """Create record based on dump."""
        record = cls.create_record(
            dump, model, pid_provider, legacy_id_key=legacy_id_key
        )
        return record

    @classmethod
    def create_record(
        cls, dump, model, pid_provider, legacy_id_key="legacy_recid"
    ):
        """Create a new record from dump."""
        if legacy_id_key is None:
            legacy_id_key = "pid"
        try:
            with db.session.begin_nested():
                record_uuid = uuid.uuid4()
                provider = pid_provider.create(
                    object_type="rec",
                    object_uuid=record_uuid,
                )
                dump["pid"] = provider.pid.pid_value
                record = model.create(dump, record_uuid)
                record.commit()
            db.session.commit()
            return record
        except IlsValidationError as e:
            click.secho("VALIDATION ERROR", fg="blue")
            click.secho(
                "RECID {0} did not pass validation. ERROR: \n {1}".format(
                    dump[legacy_id_key],
                    [
                        "{0}: {1}".format(
                            error.res["field"], error.res["message"]
                        )
                        for error in e.errors
                    ],
                ).join("\n"),
                fg="blue",
            )
            click.secho(e.original_exception.message, fg="blue")
            db.session.rollback()
            raise e
