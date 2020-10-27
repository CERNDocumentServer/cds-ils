# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# invenio-app-ils is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS mail tasks."""

from celery import shared_task
from flask import current_app
from invenio_app_ils.circulation.search import get_active_loans_by_patron_pid
from invenio_app_ils.mail.tasks import send_ils_email
from invenio_app_ils.proxies import current_app_ils

from cds_ils.mail.messages import UserDeletionWarningActiveLoanMessage


@shared_task
def send_warning_mail_patron_has_active_loans(patron_pid):
    """Send email to librarians user cannot be deleted because active loans.

    :param patron_pid: the pid of the patron.
    :param message_ctx: any other parameter to be passed as ctx in the msg.
    """
    Patron = current_app_ils.patron_cls
    patron = Patron.get_patron(patron_pid)
    loans = [
        loan.to_dict()
        for loan in get_active_loans_by_patron_pid(patron_pid).scan()
    ]

    if len(loans) > 0:  # Email is sent only if there are active loans
        recipients = current_app.config[
            "ILS_MAIL_NOTIFY_MANAGEMENT_RECIPIENTS"
        ]
        msg = UserDeletionWarningActiveLoanMessage(
            patron, loans, recipients=recipients
        )
        send_ils_email(msg)
