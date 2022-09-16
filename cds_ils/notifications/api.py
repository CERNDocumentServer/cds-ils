# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2022 CERN.
#
# invenio-app-ils is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS mail message objects."""

import json
import os

from flask import current_app
from invenio_app_ils.notifications.api import _get_notification_backends
from invenio_app_ils.notifications.messages import NotificationMsg


class AlarmMessage(NotificationMsg):
    """Message for alarms."""

    def __init__(self, name, error_msg, exception_msg, **kwargs):
        """Constructor."""
        super().__init__(
            template=os.path.join(
                "cds_ils_notifications",
                "cds_ils_alarm.html",
            ),
            ctx=dict(
                name=name,
                error_msg=error_msg,
                exception_msg=exception_msg,
                **kwargs,
            ),
            **kwargs,
        )


class UserDeletionWarningActiveLoanMessage(NotificationMsg):
    """Message user deletion warning active loans."""

    def __init__(self, patrons, **kwargs):
        """Constructor."""
        super().__init__(
            template=os.path.join(
                "cds_ils_notifications",
                "cds_ils_user_deletion_warning_active_loans.html",
            ),
            ctx=dict(patrons=patrons, **kwargs),
            **kwargs,
        )


def send_not_logged_notification(recipients, msg, **kwargs):
    """Send a notification using the configured backend(s)."""
    backends = _get_notification_backends(**kwargs)
    if not backends:
        return

    # create a serializable version of the msg for Celery tasks
    serializable_msg = msg.to_dict()
    serializable_msg.update(
        dict(
            is_manually_triggered=kwargs.pop("is_manually_triggered", False),
            main_recipient=recipients[0],
        )
    )
    # log before sending
    log_msg = dict(
        name="notification",
        action="before_send",
        message_id=serializable_msg["id"],
        data=serializable_msg,
    )
    current_app.logger.info(json.dumps(log_msg, sort_keys=True))

    for send in backends:
        # send notification in a Celery task
        send.apply_async(
            args=[recipients, serializable_msg],
            kwargs=kwargs,
        )
