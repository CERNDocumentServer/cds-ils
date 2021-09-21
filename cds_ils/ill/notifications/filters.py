# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-IlS ILL notifications filters."""


def ill_notifications_filter(record, action, **kwargs):
    """Filter notifications.

    Returns if the notification should be sent for given action
    """
    action_filter_map = {
        "extension_accepted": False,
        "extension_declined": False,
        "extension_requested": True,
    }
    return action_filter_map[action]
