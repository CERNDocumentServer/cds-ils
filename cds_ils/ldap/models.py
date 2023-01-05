# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Database models for ldap synchronizations."""

import enum
from datetime import datetime

from invenio_db import db
from sqlalchemy import Enum


class Agent(enum.Enum):
    """An agent performing an action."""

    CLI = "CLI"
    """The command line utility."""

    CELERY = "CELERY"
    """The system, from a scheduled task."""


class TaskStatus(enum.Enum):
    """The status of a task."""

    RUNNING = "RUNNING"
    """The task is currently running."""

    SUCCEEDED = "SUCCEEDED"
    """The task has successfully completed its execution."""

    FAILED = "FAILED"
    """The task was aborted due to an error."""


class LdapSynchronizationLog(db.Model):
    """Store the ldap synchronization task history."""

    __tablename__ = "ldap_sync"

    id = db.Column(db.Integer, primary_key=True)

    agent = db.Column(Enum(Agent), nullable=False)
    """The agent that initiated the task."""

    task_id = db.Column(db.String, nullable=True)
    """The task identifier, in case of a celery task."""

    status = db.Column(Enum(TaskStatus), nullable=False, default=TaskStatus.RUNNING)
    """The current status of the task."""

    start_time = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now())
    """Task start time."""

    end_time = db.Column(db.DateTime, nullable=True)
    """Task end time (if not currently running)."""

    message = db.Column(db.String, nullable=True)
    """Message in case of an error."""

    ldap_fetch_count = db.Column(db.Integer, nullable=True)
    """Number of users fetched from LDAP."""

    ils_update_count = db.Column(db.Integer, nullable=True)
    """Number of users updated in ILS."""

    ils_deletion_count = db.Column(db.Integer, nullable=True)
    """Number of users deleted from ILS."""

    ils_insertion_count = db.Column(db.Integer, nullable=True)
    """Number of users added in ILS."""

    @classmethod
    def __create(cls, data):
        """Create a new log entry."""
        log = cls(**data)
        db.session.add(log)
        db.session.commit()
        return log

    @classmethod
    def create_cli(cls):
        """Create a new log entry for a task started from the command line."""
        return cls.__create(dict(agent=Agent.CLI))

    @classmethod
    def create_celery(cls, task_id):
        """Create a new log entry for a task triggered by cron."""
        return cls.__create(
            dict(
                agent=Agent.CELERY,
                task_id=task_id,
            )
        )

    def is_running(self):
        """Check if the task is currently running."""
        return self.status == TaskStatus.RUNNING

    def set_succeeded(
        self,
        ldap_fetch_count,
        ils_update_count,
        ils_insertion_count,
    ):
        """Mark this task as complete and log output."""
        assert self.is_running()
        self.status = TaskStatus.SUCCEEDED
        self.end_time = datetime.now()
        self.ldap_fetch_count = ldap_fetch_count
        self.ils_update_count = ils_update_count
        self.ils_insertion_count = ils_insertion_count
        db.session.commit()

    def set_deletion_success(self, ldap_fetch_count, ils_deletion_count):
        """Set deletion success log."""
        assert self.is_running()
        self.status = TaskStatus.SUCCEEDED
        self.end_time = datetime.now()
        self.ldap_fetch_count = ldap_fetch_count
        self.ils_deletion_count = ils_deletion_count
        db.session.commit()

    def set_failed(self, exception):
        """Mark this task as failed."""
        assert self.is_running()
        self.status = TaskStatus.FAILED
        self.end_time = datetime.now()
        self.message = "%s: %s" % (type(exception).__name__, str(exception))
        db.session.commit()
