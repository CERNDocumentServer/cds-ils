# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Test migration utils."""
from invenio_pidstore.models import PersistentIdentifier, PIDStatus


def reindex_record(pid_type, record_class, record_indexer_class):
    """Reindex records of given pid type."""
    query = (
        x[0]
        for x in PersistentIdentifier.query.filter_by(
            object_type="rec", status=PIDStatus.REGISTERED
        )
        .filter(PersistentIdentifier.pid_type.in_((pid_type,)))
        .values(PersistentIdentifier.pid_value)
    )

    for pid in query:
        record_indexer_class.index(record_class.get_record_by_pid(pid))
