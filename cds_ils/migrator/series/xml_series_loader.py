# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Migrator Records loader."""

import logging
import uuid

import click
from flask import current_app
from invenio_app_ils.errors import IlsValidationError
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.series.api import SeriesIdProvider
from invenio_db import db

from cds_ils.migrator.utils import add_cover_metadata, clean_created_by_field
from cds_ils.minters import legacy_recid_minter

cli_logger = logging.getLogger("migrator")


class CDSSeriesDumpLoader(object):
    """Migrate a CDS Series record."""

    @classmethod
    def create(cls, dump, rectype):
        """Create record based on dump."""
        dump.prepare_revisions()
        # if we have a final revision - to remove when data cleaned.
        try:
            if dump.revisions[-1]:
                record = cls.create_record(dump, rectype)
                return record
        except IndexError as e:
            click.secho("Revision problem", fg="red")
            raise e

    @classmethod
    def create_record(cls, dump, rectype):
        """Create a new record from dump."""
        series_cls = current_app_ils.series_record_cls
        record_uuid = uuid.uuid4()
        try:
            with db.session.begin_nested():
                provider = SeriesIdProvider.create(
                    object_type="rec",
                    object_uuid=record_uuid,
                )
                timestamp, json_data = dump.revisions[-1]
                json_data["pid"] = provider.pid.pid_value
                json_data = clean_created_by_field(json_data)
                if rectype == "journal":
                    legacy_pid_type = current_app.config[
                        "CDS_ILS_RECORD_LEGACY_PID_TYPE"
                    ]
                    legacy_recid_minter(
                        json_data["legacy_recid"], legacy_pid_type, record_uuid
                    )
                add_cover_metadata(json_data)

                series = series_cls.create(json_data, record_uuid)
                series.model.created = dump.created.replace(tzinfo=None)
                series.model.updated = timestamp.replace(tzinfo=None)
                series.commit()
            db.session.commit()
            return series
        except IlsValidationError as e:
            click.secho("Field: {}".format(e.errors[0].res["field"]), fg="red")
            click.secho(e.original_exception.message, fg="red")
            raise e
