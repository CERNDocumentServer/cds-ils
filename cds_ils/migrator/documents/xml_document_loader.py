# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2018-2020 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Migrator Records loader."""

import logging
import uuid

import click
from dateutil import parser
from flask import current_app
from invenio_app_ils.documents.api import DocumentIdProvider
from invenio_app_ils.errors import IlsValidationError
from invenio_app_ils.proxies import current_app_ils
from invenio_db import db
from invenio_pidstore.errors import PIDAlreadyExists

from cds_ils.importer.documents.importer import VOCABULARIES_FIELDS
from cds_ils.importer.providers.cds.utils import (
    add_cds_url,
    add_title_from_conference_info,
)
from cds_ils.importer.vocabularies_validator import validator as vocabulary_validator
from cds_ils.literature.api import get_record_by_legacy_recid
from cds_ils.migrator.constants import CDS_ILS_FALLBACK_CREATION_DATE
from cds_ils.migrator.errors import DumpRevisionException
from cds_ils.migrator.utils import add_cover_metadata, clean_created_by_field
from cds_ils.minters import legacy_recid_minter

documents_logger = logging.getLogger("documents_logger")
files_logger = logging.getLogger("files_logger")


class CDSDocumentDumpLoader(object):
    """Migrate a CDS record.

    create and create_record has been changed to change the hardcoded
    pid_type recid to docid.
    """

    @classmethod
    def create_files(cls, record, files):
        """Dump files information instead of the file."""
        if record["_migration"]["is_yellow_report"]:
            return
        record["_migration"]["files"] = []
        for key, meta in files.items():
            obj = cls.create_file(None, key, meta)
            if obj.get("format").lower() in [".ps.gz", ".png", ".jpg", ".jpeg"]:
                continue
            # remove not needed, ES cannot handle list of lists
            del obj["recids_doctype"]
            # get filesystem path
            full_file_path = obj["full_path"].split(";")[0]
            # create a relative path
            relative_path = full_file_path.replace("/opt/cdsweb/var/data", "")
            obj["ils_relative_path"] = relative_path
            # add to the dump
            record["_migration"]["files"].append(obj)
            # log the path and recid into a file
            files_logger.error(
                f"\"{record['legacy_recid']};{full_file_path};{relative_path}\""  # noqa
            )
        if record["_migration"]["files"]:
            record["_migration"]["has_files"] = True

    @classmethod
    def create_file(cls, bucket, key, file_versions):
        """Return dict describing the latest file version."""
        return file_versions[-1]

    @classmethod
    def create(cls, dump):
        """Create record based on dump."""
        dump.prepare_revisions()
        dump.prepare_files()
        # if we have a final revision - to remove when data cleaned.
        try:
            if dump.revisions[-1]:
                record = cls.create_record(dump)

                if dump.files:
                    cls.create_files(record, dump.files)
                    record.commit()
                    db.session.commit()

                return record
        except IndexError as e:
            raise DumpRevisionException("CANNOT CREATE DUMP REVISION")

    @classmethod
    def create_record(cls, dump):
        """Create a new record from dump."""
        document_cls = current_app_ils.document_record_cls
        record_uuid = uuid.uuid4()

        timestamp, json_data = dump.revisions[-1]
        json_data = clean_created_by_field(json_data)
        vocabulary_validator.validate(VOCABULARIES_FIELDS, json_data)
        add_cover_metadata(json_data)
        add_title_from_conference_info(json_data)
        add_cds_url(json_data)

        try:
            with db.session.begin_nested():
                # checks if the document with this legacy_recid already exists
                legacy_pid_type = current_app.config["CDS_ILS_RECORD_LEGACY_PID_TYPE"]
                # First mint the legacy_recid before assigning the pid. In case
                # it fails while importing an existing record we will update it
                # and don't want the new pid, since there is already one there
                legacy_recid_minter(
                    json_data["legacy_recid"], legacy_pid_type, record_uuid
                )

                provider = DocumentIdProvider.create(
                    object_type="rec",
                    object_uuid=record_uuid,
                )
                # requirement from the library
                if (
                    json_data["_migration"]["has_journal"]
                    and json_data["document_type"] != "PROCEEDINGS"
                ):
                    json_data["document_type"] = "SERIAL_ISSUE"
                json_data["pid"] = provider.pid.pid_value
                document = document_cls.create(json_data, record_uuid)

                created_date = json_data.get("_created", CDS_ILS_FALLBACK_CREATION_DATE)

                document.model.created = parser.parse(created_date)
                document.model.updated = timestamp.replace(tzinfo=None)
                document.commit()
            db.session.commit()
            documents_logger.info(
                "CREATED",
                extra=dict(
                    legacy_id=json_data["legacy_recid"],
                    new_pid=document["pid"],
                    status="SUCCESS",
                ),
            )
            return document
        except IlsValidationError as e:
            click.secho("Field: {}".format(e.errors[0].res["field"]), fg="red")
            click.secho(e.original_exception.message, fg="red")
            raise e
        except PIDAlreadyExists as e:
            allow_updates = current_app.config.get("CDS_ILS_MIGRATION_ALLOW_UPDATES")
            if not allow_updates:
                raise e
            # update document if already exists with legacy_recid
            legacy_pid_type = current_app.config["CDS_ILS_RECORD_LEGACY_PID_TYPE"]
            # When updating we don't want to change the pid
            if "pid" in json_data:
                del json_data["pid"]
            document = get_record_by_legacy_recid(
                document_cls, legacy_pid_type, json_data["legacy_recid"]
            )
            document.update(json_data)
            document.model.updated = timestamp.replace(tzinfo=None)
            document.commit()
            db.session.commit()

            documents_logger.info(
                "UPDATED",
                extra=dict(
                    legacy_id=json_data["legacy_recid"],
                    new_pid=document["pid"],
                    status="SUCCESS",
                ),
            )
            return document
