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

import arrow
import click
from cds_dojson.marc21 import marc21
from cds_dojson.marc21.fields.books.errors import (
    ManualMigrationRequired,
    MissingRequiredField,
    UnexpectedValue,
)
from cds_dojson.marc21.utils import create_record
from flask import current_app
from invenio_app_ils.documents.api import DocumentIdProvider
from invenio_app_ils.errors import IlsValidationError
from invenio_app_ils.proxies import current_app_ils
from invenio_db import db
from invenio_migrator.records import RecordDump, RecordDumpLoader
from invenio_migrator.utils import disable_timestamp
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from cds_ils.migrator.errors import LossyConversion
from cds_ils.migrator.handlers import migration_exception_handler
from cds_ils.migrator.utils import (
    clean_created_by_field,
    process_fireroles,
    update_access,
)
from cds_ils.minters import legacy_recid_minter

cli_logger = logging.getLogger("migrator")


class CDSRecordDump(RecordDump):
    """CDS record dump class."""

    def __init__(
        self,
        data,
        source_type="marcxml",
        latest_only=False,
        pid_fetchers=None,
        dojson_model=marc21,
    ):
        """Initialize."""
        super(self.__class__, self).__init__(
            data, source_type, latest_only, pid_fetchers, dojson_model
        )

    @property
    def collection_access(self):
        """Calculate the value of the `_access` key.

        Due to the way access rights were defined in Invenio legacy we can only
        calculate the value of this key at the moment of the dump, therefore
        only the access rights are correct for the last version.
        """
        read_access = set()
        if self.data["collections"]:
            for coll, restrictions in self.data["collections"][
                "restricted"
            ].items():
                read_access.update(restrictions["users"])
                read_access.update(
                    process_fireroles(restrictions["fireroles"])
                )
            read_access.discard(None)

        return {"read": list(read_access)}

    def _prepare_intermediate_revision(self, data):
        """Convert intermediate versions to marc into JSON."""
        dt = arrow.get(data["modification_datetime"]).datetime

        if self.source_type == "marcxml":
            marc_record = create_record(data["marcxml"])
            return dt, marc_record
        else:
            val = data["json"]

        # MARC21 versions of the record are only accessible to admins
        val["_access"] = {
            "read": ["cds-admin@cern.ch"],
            "update": ["cds-admin@cern.ch"],
        }

        return dt, val

    def _prepare_final_revision(self, data):
        dt = arrow.get(data["modification_datetime"]).datetime

        exception_handlers = {
            UnexpectedValue: migration_exception_handler,
            MissingRequiredField: migration_exception_handler,
            ManualMigrationRequired: migration_exception_handler,
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
                update_access(val, self.collection_access)
                return dt, val
            except LossyConversion as e:
                current_app.logger.error(
                    "MIGRATION RULE MISSING {0} - {1}".format(
                        e.missing, marc_record
                    )
                )
                # TODO uncomment when data cleaner
                # raise e
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
            update_access(val, self.collection_access)
            return dt, val

    def prepare_revisions(self):
        """Prepare data.

        We don't convert intermediate versions to JSON to avoid conversion
        errors and get a lossless version migration.

        If the revisions is the last one, an error will be generated if the
        final translation is not complete.
        """
        # Prepare revisions
        self.revisions = []

        it = (
            [self.data["record"][0]]
            if self.latest_only
            else self.data["record"]
        )

        for i in it[:-1]:
            self.revisions.append(self._prepare_intermediate_revision(i))

        self.revisions.append(self._prepare_final_revision(it[-1]))


class CDSRecordDumpLoader:
    """Migrate a CDS records."""

    @classmethod
    def create(cls, dump, model, pid_provider, legacy_id_key="legacy_recid"):
        """Create record based on dump."""
        record = cls.create_record(
            dump, model, pid_provider, legacy_id_key=legacy_id_key
        )
        return record

    @classmethod
    @disable_timestamp
    def create_record(
        cls, dump, model, pid_provider, legacy_id_key="legacy_recid"
    ):
        """Create a new record from dump."""
        # Reserve record identifier, create record and recid pid in one
        # operation.
        record_uuid = uuid.uuid4()
        provider = pid_provider.create(
            object_type="rec",
            object_uuid=record_uuid,
        )
        dump["pid"] = provider.pid.pid_value
        if legacy_id_key is None:
            legacy_id_key = "pid"
        try:
            record = model.create(dump, record_uuid)
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
            # TODO uncomment when data cleaner - needed for testing on dev
            # raise e


class CDSDocumentDumpLoader(RecordDumpLoader):
    """Migrate a CDS record.

    create and create_record has been changed to change the hardcoded
    pid_type recid to docid.
    """

    @classmethod
    def create_files(cls, record, files, existing_files):
        """Dump files information instead of the file."""
        record["_migration"]["files"] = []
        for key, meta in files.items():
            obj = cls.create_file(None, key, meta)
            # remove not needed, ES cannot handle list of lists
            del obj["recids_doctype"]
            record["_migration"]["files"].append(obj)
        if record["_migration"]["files"]:
            record["_migration"]["has_files"] = True

    @classmethod
    def create_file(cls, bucket, key, file_versions):
        """Return dict describing the latest file version."""
        return file_versions[-1]

    @classmethod
    def create(cls, dump):
        """Create record based on dump."""
        # If 'record' is not present, just create the PID
        if not dump.data.get("record"):
            try:
                PersistentIdentifier.get(
                    pid_type="docid", pid_value=dump.recid
                )
            except PIDDoesNotExistError:
                PersistentIdentifier.create(
                    "docid", dump.recid, status=PIDStatus.RESERVED
                )
                db.session.commit()
            return None

        dump.prepare_revisions()
        dump.prepare_pids()
        dump.prepare_files()
        # if we have a final revision - to remove when data cleaned.
        try:
            if dump.revisions[-1]:
                record = cls.create_record(dump)

                if dump.files:
                    cls.create_files(record, dump.files, existing_files=None)
                    record.commit()
                    db.session.commit()

                return record
        except IndexError as e:
            click.secho("Revision problem", fg="red")

    @classmethod
    @disable_timestamp
    def create_record(cls, dump):
        """Create a new record from dump."""
        # Reserve record identifier, create record and recid pid in one
        # operation.
        record_uuid = uuid.uuid4()
        provider = DocumentIdProvider.create(
            object_type="rec",
            object_uuid=record_uuid,
        )
        timestamp, json_data = dump.revisions[-1]
        json_data["pid"] = provider.pid.pid_value
        json_data = clean_created_by_field(json_data)

        if json_data["legacy_recid"] == 262146:
            leg_recid_pid = PersistentIdentifier.create(
                pid_type="docid",
                pid_value=json_data["legacy_recid"],
                object_type="rec",
                object_uuid=record_uuid,
                status=PIDStatus.REGISTERED,
            )
            leg_recid_pid.redirect(provider.pid)
        else:
            legacy_recid_minter(
                json_data["legacy_recid"], provider.pid, record_uuid
            )
        click.secho("redirect!!!!", fg="red")
        try:
            Document = current_app_ils.document_record_cls
            document = Document.create(json_data, record_uuid)
            document.model.created = dump.created.replace(tzinfo=None)
            document.model.updated = timestamp.replace(tzinfo=None)
            document.commit()
            db.session.commit()

            return document
        except IlsValidationError as e:
            click.secho("Field: {}".format(e.errors[0].res["field"]), fg="red")
            click.secho(e.original_exception.message, fg="red")
            raise e
