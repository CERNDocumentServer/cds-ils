# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS minters."""

from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from cds_ils.documents.api import DOCUMENT_LEGACY_PID_TYPE


def legacy_recid_minter(legacy_recid, pid, uuid):
    """Legacy_recid minter."""
    leg_recid_pid = PersistentIdentifier.create(
        # pid_type="docid",
        pid_type=DOCUMENT_LEGACY_PID_TYPE,
        pid_value=legacy_recid,
        object_type="rec",
        object_uuid=uuid,
        status=PIDStatus.REGISTERED,
    )
    leg_recid_pid.redirect(pid)
