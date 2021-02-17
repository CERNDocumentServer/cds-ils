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
from flask import current_app
from invenio_app_ils.errors import IlsValidationError
from invenio_db import db
from invenio_pidstore.errors import PIDAlreadyExists

from cds_ils.literature.api import get_record_by_legacy_recid
from cds_ils.minters import legacy_recid_minter

cli_logger = logging.getLogger("migrator")


class CDSRecordDumpLoader(object):
    """Migrate a CDS records.

    This class is focused on migrating files from a json file (not MARC),
    fe: ILLs, Acqs, Loans.
    """

    @classmethod
    def create(cls, dump, model, pid_provider, legacy_id_key="legacy_recid"):
        """Create record based on dump."""
        record = cls.create_record(
            dump, model, pid_provider, legacy_id_key=legacy_id_key
        )
        return record

    @classmethod
    def get_legacy_pid_type_by_provider(cls, provider):
        """Get mintable legacy pid type based on provider pid type."""
        config = current_app.config
        mintable_pids_map = {
            "pitmid": config["CDS_ILS_ITEM_LEGACY_PID_TYPE"],
            "illbid": config["CDS_ILS_BORROWING_REQ_LEGACY_PID_TYPE"],
            "acqoid": config["CDS_ILS_ACQ_ORDER_LEGACY_PID_TYPE"],
        }
        return mintable_pids_map.get(provider.pid.pid_type, None)

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
                legacy_pid_type = cls.get_legacy_pid_type_by_provider(provider)

                if legacy_pid_type:
                    legacy_recid_minter(
                        dump[legacy_id_key], legacy_pid_type, record_uuid
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
        except PIDAlreadyExists as e:
            allow_updates = current_app.config.get(
                "CDS_ILS_MIGRATION_ALLOW_UPDATES"
            )
            if not allow_updates:
                raise e
            if legacy_pid_type:
                # update record if already exists with legacy_recid
                record = get_record_by_legacy_recid(
                    model, legacy_pid_type, dump[legacy_id_key]
                )
                record.update(dump)
                record.commit()
                db.session.commit()
                return record
