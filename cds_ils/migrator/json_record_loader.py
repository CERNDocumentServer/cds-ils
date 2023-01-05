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

from dateutil import parser
from flask import current_app
from invenio_app_ils.errors import IlsValidationError
from invenio_app_ils.proxies import current_app_ils
from invenio_db import db
from invenio_pidstore.errors import PIDAlreadyExists

from cds_ils.literature.api import get_record_by_legacy_recid
from cds_ils.migrator.constants import CDS_ILS_FALLBACK_CREATION_DATE
from cds_ils.migrator.utils import (
    get_legacy_pid_type_by_provider,
    model_provider_by_rectype,
)
from cds_ils.minters import legacy_recid_minter


class CDSRecordDumpLoader(object):
    """Migrate a CDS records.

    This class is focused on migrating files from a json file (not MARC),
    fe: ILLs, Acqs, Loans.
    """

    @classmethod
    def create(cls, dump, rectype, legacy_id, mint_legacy_pid=True, log_extra={}):
        """Create record based on dump."""
        return cls.create_record(
            dump,
            rectype,
            legacy_id=legacy_id,
            mint_legacy_pid=mint_legacy_pid,
            log_extra=log_extra,
        )

    @classmethod
    def create_record(
        cls, dump, rectype, legacy_id, mint_legacy_pid=True, log_extra={}
    ):
        """Create a new record from dump."""
        records_logger = logging.getLogger(f"{rectype}s_logger")
        model, pid_provider = model_provider_by_rectype(rectype)

        document_class = current_app_ils.document_record_cls
        series_class = current_app_ils.series_record_cls

        try:
            with db.session.begin_nested():
                record_uuid = uuid.uuid4()
                provider = pid_provider.create(
                    object_type="rec",
                    object_uuid=record_uuid,
                )
                dump["pid"] = provider.pid.pid_value
                if mint_legacy_pid:
                    legacy_pid_type = get_legacy_pid_type_by_provider(provider)
                    legacy_recid_minter(legacy_id, legacy_pid_type, record_uuid)
                record = model.create(dump, record_uuid)
                if isinstance(record, document_class) or isinstance(
                    record, series_class
                ):
                    created_date = dump.get("_created", CDS_ILS_FALLBACK_CREATION_DATE)
                    record.model.created = parser.parse(created_date)
                record.commit()
            db.session.commit()
            records_logger.info(
                "CREATED",
                extra=dict(
                    new_pid=record["pid"],
                    status="SUCCESS",
                    legacy_id=legacy_id,
                    **log_extra,
                ),
            )
            return record
        except IlsValidationError as e:
            db.session.rollback()
            raise e
        except PIDAlreadyExists as e:
            allow_updates = current_app.config.get("CDS_ILS_MIGRATION_ALLOW_UPDATES")
            if not allow_updates:
                raise e
            if legacy_pid_type:
                # update record if already exists with legacy_recid
                record = get_record_by_legacy_recid(model, legacy_pid_type, legacy_id)
                # When updating we don't want to change the pid
                if "pid" in dump:
                    del dump["pid"]
                record.update(dump)
                record.commit()
                db.session.commit()
                records_logger.info(
                    "UPDATED",
                    extra=dict(
                        new_pid=record["pid"],
                        status="SUCCESS",
                        legacy_id=legacy_id,
                        **log_extra,
                    ),
                )
                return record
