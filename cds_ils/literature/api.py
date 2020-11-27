# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS literature API."""

from invenio_pidstore.resolver import Resolver

from cds_ils.config import RECORD_LEGACY_PID_TYPE


def get_record_by_legacy_recid(cls, pid_value):
    """Get ils record by pid value and pid type."""
    resolver = Resolver(
        pid_type=RECORD_LEGACY_PID_TYPE,
        object_type="rec",
        getter=cls.get_record,
    )
    _, record = resolver.resolve(str(pid_value))
    return record
