# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS literature API."""
from invenio_pidstore.resolver import Resolver


def get_record_by_legacy_recid(cls, legacy_pid_type, pid_value):
    """Get ils record by pid value and pid type."""
    resolver = Resolver(
        pid_type=legacy_pid_type,
        object_type="rec",
        getter=cls.get_record,
    )
    pid, record = resolver.resolve(str(pid_value))
    return record
