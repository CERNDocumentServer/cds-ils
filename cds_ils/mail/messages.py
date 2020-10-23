# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# invenio-app-ils is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS mail message objects."""

import os

from invenio_app_ils.mail.messages import BlockTemplatedMessage


class UserDeletionWarningActiveLoanMessage(BlockTemplatedMessage):
    """Message user deletion warning active loans."""

    def __init__(self, patron, loans, **kwargs):
        """Constructor."""
        super().__init__(
            template=os.path.join(
                "cds_ils_mails",
                "cds_ils_user_deletion_warning_active_loans.html",
            ),
            ctx=dict(patron=patron, loans=loans, **kwargs),
            **kwargs,
        )
