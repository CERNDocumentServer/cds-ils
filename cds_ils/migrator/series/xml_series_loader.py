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
from dateutil import parser
from flask import current_app
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.series.api import SeriesIdProvider
from invenio_db import db
from invenio_pidstore.errors import PIDAlreadyExists

from cds_ils.importer.providers.cds.utils import add_cds_url
from cds_ils.importer.series.importer import VOCABULARIES_FIELDS
from cds_ils.importer.vocabularies_validator import validator as vocabulary_validator
from cds_ils.literature.api import get_record_by_legacy_recid
from cds_ils.migrator.constants import CDS_ILS_FALLBACK_CREATION_DATE
from cds_ils.migrator.series.api import serial_already_exists
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
        records_logger = logging.getLogger(f"{rectype}s_logger")
        series_cls = current_app_ils.series_record_cls
        record_uuid = uuid.uuid4()

        try:
            with db.session.begin_nested():
                timestamp, json_data = dump.revisions[-1]

                if rectype == "serial" and serial_already_exists(json_data["title"]):
                    return

                json_data = clean_created_by_field(json_data)
                vocabulary_validator.validate(VOCABULARIES_FIELDS, json_data)

                provider = SeriesIdProvider.create(
                    object_type="rec",
                    object_uuid=record_uuid,
                )

                add_cds_url(json_data)
                json_data["pid"] = provider.pid.pid_value

                if rectype == "journal":
                    legacy_pid_type = current_app.config[
                        "CDS_ILS_SERIES_LEGACY_PID_TYPE"
                    ]
                    legacy_recid_minter(
                        json_data["legacy_recid"], legacy_pid_type, record_uuid
                    )
                add_cover_metadata(json_data)
                series = series_cls.create(json_data, record_uuid)
                created_date = json_data.get("_created", CDS_ILS_FALLBACK_CREATION_DATE)
                series.model.created = parser.parse(created_date)
                series.model.updated = timestamp.replace(tzinfo=None)
                series.commit()
            db.session.commit()
            records_logger.info(
                "CREATED",
                extra=dict(
                    new_pid=series["pid"],
                    status="SUCCESS",
                    legacy_id=json_data["legacy_recid"],
                ),
            )
            return series
        except PIDAlreadyExists as e:
            allow_updates = current_app.config.get("CDS_ILS_MIGRATION_ALLOW_UPDATES")
            if not allow_updates:
                raise e
            # update document if already exists with legacy_recid
            legacy_pid_type = current_app.config["CDS_ILS_SERIES_LEGACY_PID_TYPE"]
            # When updating we don't want to change the pid
            if "pid" in json_data:
                del json_data["pid"]
            series = get_record_by_legacy_recid(
                series_cls, legacy_pid_type, json_data["legacy_recid"]
            )
            series.update(json_data)
            series.model.updated = timestamp.replace(tzinfo=None)
            series.commit()
            db.session.commit()

            records_logger.info(
                "UPDATED",
                extra=dict(
                    legacy_id=json_data["legacy_recid"],
                    new_pid=series["pid"],
                    status="SUCCESS",
                ),
            )
            return series
