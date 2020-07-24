# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Migrator Records loader."""

from __future__ import absolute_import, print_function

import datetime
import logging
import uuid

import arrow
import click
from cds_dojson.marc21 import marc21
from cds_dojson.marc21.fields.books.errors import ManualMigrationRequired, \
    MissingRequiredField, UnexpectedValue
from cds_dojson.marc21.utils import create_record
from flask import current_app
from invenio_app_ils.documents.api import Document, DocumentIdProvider
from invenio_app_ils.errors import IlsValidationError
from invenio_db import db
from invenio_migrator.records import RecordDump, RecordDumpLoader
from invenio_migrator.utils import disable_timestamp
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records import Record

from cds_books.migrator.errors import LossyConversion
from cds_books.migrator.handlers import migration_exception_handler
from cds_books.migrator.utils import process_fireroles, update_access

cli_logger = logging.getLogger('migrator')


class CDSRecordDump(RecordDump):
    """CDS record dump class."""

    def __init__(self,
                 data,
                 source_type='marcxml',
                 latest_only=False,
                 pid_fetchers=None,
                 dojson_model=marc21):
        """Initialize."""
        super(self.__class__, self).__init__(data, source_type, latest_only,
                                             pid_fetchers, dojson_model)
        cli_logger.info('\n=====#RECID# {0} INIT=====\n'.format(data['recid']))

    @property
    def collection_access(self):
        """Calculate the value of the `_access` key.

        Due to the way access rights were defined in Invenio legacy we can only
        calculate the value of this key at the moment of the dump, therefore
        only the access rights are correct for the last version.
        """
        read_access = set()
        if self.data['collections']:
            for coll, restrictions in \
                    self.data['collections']['restricted'].items():
                read_access.update(restrictions['users'])
                read_access.update(
                    process_fireroles(restrictions['fireroles']))
            read_access.discard(None)

        return {'read': list(read_access)}

    def _prepare_intermediate_revision(self, data):
        """Convert intermediate versions to marc into JSON."""
        dt = arrow.get(data['modification_datetime']).datetime

        if self.source_type == 'marcxml':
            marc_record = create_record(data['marcxml'])
            return dt, marc_record
        else:
            val = data['json']

        # MARC21 versions of the record are only accessible to admins
        val['_access'] = {
            'read': ['cds-admin@cern.ch'],
            'update': ['cds-admin@cern.ch']
        }

        return dt, val

    def _prepare_final_revision(self, data):
        dt = arrow.get(data['modification_datetime']).datetime

        exception_handlers = {
            UnexpectedValue: migration_exception_handler,
            MissingRequiredField: migration_exception_handler,
            ManualMigrationRequired: migration_exception_handler,
        }

        if self.source_type == 'marcxml':
            marc_record = create_record(data['marcxml'])
            try:
                val = self.dojson_model.do(
                    marc_record, exception_handlers=exception_handlers)
                missing = self.dojson_model.missing(marc_record)
                if missing:
                    raise LossyConversion(missing=missing)
                update_access(val, self.collection_access)
                return dt, val
            except LossyConversion as e:
                current_app.logger.error(
                    'MIGRATION RULE MISSING {0} - {1}'.format(
                        e.missing, marc_record))
                # TODO uncomment when data cleaner
                # raise e
            except Exception as e:
                current_app.logger.error(
                    'Impossible to convert to JSON {0} - {1}'.format(
                        e, marc_record))
                raise e
        else:
            val = data['json']

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

        it = [self.data['record'][0]] if self.latest_only \
            else self.data['record']

        for i in it[:-1]:
            self.revisions.append(self._prepare_intermediate_revision(i))

        self.revisions.append(self._prepare_final_revision(it[-1]))


class CDSParentRecordDump(RecordDump):
    """Dump CDS parent record."""

    def _prepare_revision(self, data):
        """Prepare data."""
        dt = datetime.datetime.utcnow()

        val = data
        val['_collections'] = self.data.get('collections', [])

        return dt, val

    def prepare_revisions(self):
        """Prepare record revisions for migration."""
        self.revisions = [self.data]


class CDSParentRecordDumpLoader(RecordDumpLoader):
    """Migrate a CDS parent records."""

    @classmethod
    def create(cls, dump, model, pid_provider):
        """Create record based on dump."""
        record = cls.create_record(dump, model, pid_provider)
        return record

    @classmethod
    @disable_timestamp
    def create_record(cls, dump, model, pid_provider):
        """Create a new record from dump."""
        # Reserve record identifier, create record and recid pid in one
        # operation.
        record_uuid = uuid.uuid4()
        provider = pid_provider.create(
            object_type='rec',
            object_uuid=record_uuid,
        )
        dump['pid'] = provider.pid.pid_value
        try:
            record = model.create(dump, record_uuid)
            record.model.created = datetime.datetime.utcnow()
            record.commit()
            return record
        except IlsValidationError as e:
            click.secho("RECID {0} did not pass validation. ERROR: \n {1}"
                        .format(dump['legacy_recid'], e), fg='red')
            # TODO uncomment when data cleaner - needed for testing on dev
            # raise e


class CDSDocumentDumpLoader(RecordDumpLoader):
    """Migrate a CDS record.

    create and create_record has been changed to change the hardcoded pid_type
    recid to docid.
    """

    @classmethod
    def create_files(cls, *args, **kwargs):
        """Disable the files load."""
        pass

    @classmethod
    def create(cls, dump):
        """Create record based on dump."""
        # If 'record' is not present, just create the PID
        if not dump.data.get('record'):
            try:
                PersistentIdentifier.get(pid_type='docid',
                                         pid_value=dump.recid)
            except PIDDoesNotExistError:
                PersistentIdentifier.create(
                    'docid', dump.recid,
                    status=PIDStatus.RESERVED
                )
                db.session.commit()
            return None

        dump.prepare_revisions()
        dump.prepare_pids()
        dump.prepare_files()
        # if we have a final revision - to remove when data cleaned.
        if dump.rest[-1]:
            record = cls.create_record(dump)

            return record

    @classmethod
    @disable_timestamp
    def create_record(cls, dump):
        """Create a new record from dump."""
        # Reserve record identifier, create record and recid pid in one
        # operation.
        timestamp, data = dump.latest
        record = Record.create(data)
        record_uuid = uuid.uuid4()
        provider = DocumentIdProvider.create(
            object_type='rec',
            object_uuid=record_uuid,
        )
        # -1 should mean the latest revision
        timestamp, json_data = dump.rest[-1]
        json_data['pid'] = provider.pid.pid_value
        record.model.json = json_data
        record.model.created = dump.created.replace(tzinfo=None)
        record.model.updated = timestamp.replace(tzinfo=None)
        try:
            document = Document.create(record.model.json, record_uuid)
            document.commit()
            db.session.commit()

            return document
        except IlsValidationError as e:
            click.secho(e.original_exception.message, fg='red')
            # TODO uncomment when data cleaner - needed for testing on dev
            # raise e
