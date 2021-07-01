# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Database models for importer."""

import enum
from datetime import datetime

from invenio_db import db
from sqlalchemy import Enum


def _format_exception(exception):
    """Formats the exception into a string."""
    exception_type = type(exception).__name__
    exception_message = str(exception)
    if exception_message:
        return "{}: {}".format(exception_type, exception_message)
    else:
        return exception_type


class ImporterEnum(enum.Enum):
    """Importer enum class."""

    def __str__(self):
        """String representation."""
        return str(self.value)


class ImporterAgent(ImporterEnum):
    """An agent performing an action."""

    CLI = "CLI"
    """From the command line."""

    USER = "USER"
    """A user from the UI."""


class ImporterTaskStatus(ImporterEnum):
    """The status of a task."""

    RUNNING = "RUNNING"
    """The task is currently running."""

    SUCCEEDED = "SUCCEEDED"
    """The task has successfully completed its execution."""

    FAILED = "FAILED"
    """The task was aborted due to an error."""


class ImporterMode(ImporterEnum):
    """The mode of an importation task."""

    PREVIEW_IMPORT = "PREVIEW_IMPORT"

    PREVIEW_DELETE = "PREVIEW_DELETE"

    IMPORT = "IMPORT"

    DELETE = "DELETE"

    @classmethod
    def get_options(cls):
        """Return possible import modes."""
        cls_defined_members = cls.__members__.keys()
        return [getattr(cls, member).value for member in cls_defined_members]


class ImporterTaskLog(db.Model):
    """Store the ldap synchronization task history."""

    __tablename__ = "importer_task"

    id = db.Column(db.Integer, primary_key=True)

    agent = db.Column(Enum(ImporterAgent), nullable=False)
    """The agent that initiated the task."""

    status = db.Column(
        Enum(ImporterTaskStatus), nullable=False,
        default=ImporterTaskStatus.RUNNING
    )
    """The current status of the task."""

    provider = db.Column(db.String, nullable=False)
    """The provider of the data. Unconstrained for extensibility purposes."""

    source_type = db.Column(db.String, nullable=False)
    """The format of the source data."""

    mode = db.Column(db.Enum(ImporterMode), nullable=False)
    """The chosen importation mode."""

    original_filename = db.Column(db.String, nullable=False)
    """The original name of the imported file."""

    start_time = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now()
    )
    """Task start time."""

    end_time = db.Column(db.DateTime, nullable=True)
    """Task end time (if not currently running)."""

    message = db.Column(db.String, nullable=True)
    """Message in case of an error."""

    entries_count = db.Column(db.Integer, nullable=True)
    """Number of entries in source file."""

    @classmethod
    def create(cls, data):
        """Create a new task log."""
        log = cls(**data)
        db.session.add(log)
        db.session.commit()
        return log

    def is_running(self):
        """Check if the task is currently running."""
        return self.status == ImporterTaskStatus.RUNNING

    def set_succeeded(self):
        """Mark this task as complete and log output."""
        assert self.is_running()
        self.status = ImporterTaskStatus.SUCCEEDED
        self.end_time = datetime.now()
        db.session.commit()

    def set_failed(self, exception):
        """Mark this task as failed."""
        assert self.is_running()
        self.status = ImporterTaskStatus.FAILED
        self.end_time = datetime.now()
        self.message = _format_exception(exception)
        db.session.commit()

    def set_entries_count(self, entries):
        """Set logged entries count."""
        self.entries_count = len(entries)
        db.session.commit()


class ImportRecordLog(db.Model):
    """Entry log of one imported record."""

    id = db.Column(db.Integer, primary_key=True)
    __tablename__ = "import_record_log"

    # Ensure the entries are uniquely defined
    __table_args__ = (db.UniqueConstraint('import_id', 'entry_recid'),)

    import_id = db.Column(db.Integer, db.ForeignKey('importer_task.id',
                                                    ondelete="CASCADE"))
    """The parent task."""

    entry_recid = db.Column(db.String, nullable=False)
    """The index of the entry in the source."""

    error = db.Column(db.String, nullable=True)
    """In case of an error."""

    importer_task = db.relationship(
        ImporterTaskLog,
        backref=db.backref('records', lazy='dynamic', passive_deletes=True)
    )
    """Relationship."""

    document_json = db.Column(db.JSON, nullable=True)
    document = db.Column(db.JSON, nullable=True)
    raw_json = db.Column(db.JSON, nullable=True)
    output_pid = db.Column(db.String, nullable=True)
    action = db.Column(db.String, nullable=True)
    partial_matches = db.Column(db.JSON, nullable=True)
    eitem = db.Column(db.JSON, nullable=True)
    series = db.Column(db.JSON, nullable=True)

    # default ordering
    __mapper_args__ = {
        "order_by": id
    }

    @classmethod
    def __create(cls, data):
        """Create a new entry."""
        entry = cls(**data)
        db.session.add(entry)
        db.session.commit()
        return entry

    @classmethod
    def create_success(cls, import_id, entry_recid, report):
        """Mark this record as successfully imported."""
        return cls.__create(
            {
                **dict(import_id=import_id,
                       entry_recid=entry_recid),
                **report
            }
        )

    @classmethod
    def create_failure(cls, import_id, entry_recid, exception, report={}):
        """Mark this record as failed."""
        return cls.__create(
            {
                **dict(import_id=import_id,
                       entry_recid=entry_recid,
                       error=_format_exception(exception)
                       ),
                **report
            }
        )
