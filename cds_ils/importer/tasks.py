# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer tasks."""
import datetime

from celery import shared_task
from invenio_db import db
from sqlalchemy import or_

from cds_ils.importer.api import import_from_xml
from cds_ils.importer.models import ImporterAgent, ImporterMode, \
    ImporterTaskLog


def create_import_task(
    source_path, original_filename, provider, mode,
    source_type="marcxml"
):
    """Creates a task and returns its associated identifier."""
    log = ImporterTaskLog.create(
        dict(
            agent=ImporterAgent.USER,
            provider=provider,
            source_type=source_type,
            mode=mode,
            original_filename=original_filename,
        )
    )
    import_from_xml_task.apply_async(
        (
            log.id,
            source_path,
            source_type,
            provider,
            mode,
        )
    )

    return log


@shared_task
def import_from_xml_task(log_id, source_path, source_type, provider, mode):
    """Load a single xml file task."""
    log = ImporterTaskLog.query.get(log_id)
    import_from_xml(log, source_path, source_type, provider, mode)


@shared_task
def clean_preview_logs():
    """Clean stale preview logs."""
    # take tasks older than 7 days
    stale_logs_date = datetime.datetime.now() - datetime.timedelta(days=7)

    # find and delete all the stale preview logs
    ImporterTaskLog.query.filter(
        or_(ImporterTaskLog.mode == ImporterMode.PREVIEW_DELETE,
            ImporterTaskLog.mode == ImporterMode.PREVIEW_IMPORT),
        ImporterTaskLog.start_time < stale_logs_date).delete()

    db.session.commit()
