# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS minters."""

from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from cds_ils.config import RECORD_LEGACY_PID_TYPE


def legacy_recid_minter(legacy_recid, uuid):
    """Legacy_recid minter."""
    PersistentIdentifier.create(
        pid_type=RECORD_LEGACY_PID_TYPE,
        pid_value=legacy_recid,
        object_type="rec",
        object_uuid=uuid,
        status=PIDStatus.REGISTERED,
    )
