# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS minters."""
from flask import current_app
from invenio_pidstore.models import PersistentIdentifier, PIDStatus


def legacy_recid_minter(legacy_recid, uuid):
    """Legacy_recid minter."""
    legacy_pid_type = current_app.config["CDS_ILS_RECORD_LEGACY_PID_TYPE"]
    PersistentIdentifier.create(
        pid_type=legacy_pid_type,
        pid_value=legacy_recid,
        object_type="rec",
        object_uuid=uuid,
        status=PIDStatus.REGISTERED,
    )
