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

from .api import sync_users
from .models import LdapSynchronizationLog

celery_logger = get_task_logger(__name__)


@shared_task
def synchronize_users_task():
    """Add entry to database with info about this synchronization."""
    log = LdapSynchronizationLog.create_celery(
        synchronize_users_task.request.id
    )
    try:
        result = sync_users()
        log.set_succeeded(*result)
    except Exception as e:
        current_app.logger.exception(e)
        log.set_failed(e)
