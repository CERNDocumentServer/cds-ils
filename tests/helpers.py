# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Test helpers module."""
import json
import os
import uuid

from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus


def load_json_from_datadir(filename, relpath=None):
    """Load JSON from dir."""
    if relpath:
        _data_dir = os.path.join(os.path.dirname(__file__), relpath, "data")
    else:
        _data_dir = os.path.join(os.path.dirname(__file__), "data")
    with open(os.path.join(_data_dir, filename), "r") as fp:
        return json.load(fp)


def mint_record_pid(pid_type, pid_field, record, obj_uuid=None):
    """Mint the given PID for the given record."""
    if obj_uuid:
        record_uuid = obj_uuid
    else:
        record_uuid = uuid.uuid4()
    PersistentIdentifier.create(
        pid_type=pid_type,
        pid_value=record[pid_field],
        object_type="rec",
        object_uuid=record_uuid,
        status=PIDStatus.REGISTERED,
    )
    db.session.commit()
    return record_uuid


def _create_records(db, objs, cls, pid_type, is_rdm=False):
    """Create records and index."""
    recs = []
    for obj in objs:
        record_uuid = mint_record_pid(pid_type, "pid", {"pid": obj["pid"]})

        if "legacy_recid" in obj:
            mint_record_pid(
                "ldocid", "pid", {"pid": obj["legacy_recid"]}, obj_uuid=record_uuid
            )
        if is_rdm and "_rdm_pid" in obj:
            mint_record_pid(
                "cdspid", "pid", {"pid": obj["_rdm_pid"]}, obj_uuid=record_uuid
            )
        record = cls.create(obj, record_uuid)
        recs.append(record)
        db.session.commit()
    return recs
