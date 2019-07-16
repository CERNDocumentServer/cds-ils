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
from cds_dojson.marc21 import marc21
from cds_dojson.marc21.fields.books.errors import ManualMigrationRequired, \
    MissingRequiredField, UnexpectedValue
from cds_dojson.marc21.utils import create_record
from flask import current_app
from invenio_migrator.records import RecordDump, RecordDumpLoader
from invenio_migrator.utils import disable_timestamp
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
                raise e
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

    def _prepare_revision(self, data):
        """Prepare data."""
        dt = datetime.datetime.now()

        val = data
        val['_collections'] = self.data.get('collections', [])

        return dt, val

    def prepare_revisions(self):
        self.revisions = [self.data]


class CDSParentRecordDumpLoader(RecordDumpLoader):

    @classmethod
    def create(cls, dump, model=Record):
        """Create record based on dump."""
        record = cls.create_record(dump, model)
        return record

    @classmethod
    @disable_timestamp
    def create_record(cls, dump, model=Record):
        """Create a new record from dump."""
        # Reserve record identifier, create record and recid pid in one
        # operation.
        record_uuid = uuid.uuid4()
        provider = model._pid_provider.create(
            object_type='rec',
            object_uuid=record_uuid,
        )
        dump[model.pid_field] = provider.pid.pid_value
        record = model.create(dump, record_uuid)
        record.model.created = datetime.datetime.now()
        record.commit()
        return record


class CDSRecordDumpLoader(RecordDumpLoader):
    """Migrate a CDS record."""

    @classmethod
    def create_files(cls, *args, **kwargs):
        """Disable the files load."""
        pass

    @classmethod
    def create(cls, dump):
        """Update an existing record."""
        record = super(CDSRecordDumpLoader, cls).create(dump=dump)
        return record


