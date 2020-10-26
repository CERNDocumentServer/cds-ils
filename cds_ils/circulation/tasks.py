# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Circulation tasks."""

from celery.utils.log import get_task_logger
from flask import current_app
from invenio_app_ils.circulation.mail.factory import \
    loan_list_message_creator_factory
from invenio_app_ils.circulation.search import get_active_loans_by_patron_pid
from invenio_app_ils.mail.tasks import send_ils_email
from invenio_app_ils.proxies import current_app_ils

celery_logger = get_task_logger(__name__)


def send_active_loans_mail(patron_pid, message_ctx={}, **kwargs):
    """Send an email to librarian with on going loans of given patron.

    :param patron_pid: the pid of the patron.
    :param message_ctx: any other parameter to be passed as ctx in the msg.
    """
    creator = loan_list_message_creator_factory()

    Patron = current_app_ils.patron_cls
    patron = Patron.get_patron(patron_pid)
    loans = [
        loan.to_dict()
        for loan in get_active_loans_by_patron_pid(patron_pid).scan()
    ]

    if len(loans) > 0:  # Email is only sent if there are active loans
        recipient = current_app.config["MANAGEMENT_EMAIL"]
        msg = creator(
            patron,
            loans,
            message_ctx=message_ctx,
            recipients=[recipient],
            **kwargs,
        )
        send_ils_email(msg)
