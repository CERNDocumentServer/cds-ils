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
from cds_ils.importer.models import ImporterAgent, ImporterImportLog, ImporterMode


def create_import_task(
    source_path,
    original_filename,
    provider,
    mode,
    ignore_missing_rules,
    source_type="marcxml",
):
    """Creates a task and returns its associated identifier."""
    log = ImporterImportLog.create(
        dict(
            agent=ImporterAgent.USER,
            provider=provider,
            source_type=source_type,
            mode=mode,
            original_filename=original_filename,
            ignore_missing_rules=ignore_missing_rules,
        )
    )
    async_result = import_from_xml_task.apply_async(
        (log.id, source_path, source_type, provider, mode, ignore_missing_rules)
    )

    log.celery_task_id = async_result.id
    db.session.commit()

    return log


@shared_task
def import_from_xml_task(
    log_id, source_path, source_type, provider, mode, ignore_missing_rules
):
    """Load a single xml file task."""
    log = ImporterImportLog.query.get(log_id)
    import_from_xml(log, source_path, source_type, provider, mode, ignore_missing_rules)


@shared_task
def clean_preview_logs():
    """Clean stale preview logs."""
    # take tasks older than 7 days
    seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)

    # find and delete all the stale preview logs
    ImporterImportLog.query.filter(
        or_(
            ImporterImportLog.mode == ImporterMode.PREVIEW_DELETE,
            ImporterImportLog.mode == ImporterMode.PREVIEW_IMPORT,
        ),
        ImporterImportLog.start_time < seven_days_ago,
    ).delete()

    db.session.commit()
