# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-IlS Document requests notifications filters."""


def document_requests_notifications_filter(record, action, **kwargs):
    """Filter notifications.

    Returns if the notification should be sent for given action
    """
    if action == "request_declined":
        decline_reason = record.get("decline_reason", "")
        action = "{}_{}".format(action, decline_reason.lower())

    action_filter_map = {
        "request_accepted": True,
        "request_declined_in_catalog": False,
        "request_declined_not_found": False,
        "request_declined_other": False,
        "request_declined_user_cancel": True,
    }
    return action_filter_map[action]
