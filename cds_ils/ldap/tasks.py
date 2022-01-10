# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# invenio-app-ils is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Ldap tasks."""


from celery import shared_task
from celery.utils.log import get_task_logger
from flask import current_app
from invenio_db import db

from .api import delete_users, update_users
from .models import LdapSynchronizationLog

celery_logger = get_task_logger(__name__)


@shared_task
def synchronize_users_task():
    """Run the task to update users from LDAP."""
    log = LdapSynchronizationLog.create_celery(
        synchronize_users_task.request.id
    )
    try:
        result = update_users()
        log.set_succeeded(*result)
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(e)
        log.set_failed(e)


@shared_task
def anonymize_users_task():
    """Run user deletion/anonymization task."""
    log = LdapSynchronizationLog.create_celery(
        synchronize_users_task.request.id
    )

    try:
        result = delete_users(dry_run=False)
        log.set_deletion_success(*result)
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(e)
        log.set_failed(e)
