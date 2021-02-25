# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator."""
import uuid

from invenio_app_ils.acquisition.api import VENDOR_PID_TYPE
from invenio_app_ils.acquisition.proxies import current_ils_acq
from invenio_app_ils.documents.api import DOCUMENT_PID_TYPE
from invenio_app_ils.ill.api import LIBRARY_PID_TYPE
from invenio_app_ils.ill.proxies import current_ils_ill
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.series.api import SERIES_PID_TYPE
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

MIGRATION_DOCUMENT_PID = "L1t3r-4tUr3"
MIGRATION_LIBRARY_PID = "L1bR4-r1eSP"
MIGRATION_VENDOR_PID = "V3nD0-rP1dP"
MIGRATION_YELLOW_PID = "Y3lL0-R3p9R"
MIGRATION_DESIGN_PID = "d3S1g-r3P0r"


def mint_migration_records(pid_type, pid_field, data):
    """Minter for migration records."""
    record_uuid = uuid.uuid4()
    PersistentIdentifier.create(
        pid_type=pid_type,
        pid_value=data[pid_field],
        object_type="rec",
        object_uuid=record_uuid,
        status=PIDStatus.REGISTERED,
    )
    return record_uuid


def create_default_record(data, record_cls, indexer, record_pid_type):
    """Create standard record."""
    record_uuid = mint_migration_records(record_pid_type, "pid", data)
    record = record_cls.create(data, record_uuid)
    db.session.commit()
    indexer.index(record)
    return record


def create_unknown_document():
    """Create migration document."""
    data = {
        "pid": MIGRATION_DOCUMENT_PID,
        "title": "Migrated Unknown Document",
        "created_by": {"type": "script", "value": "migration"},
        "authors": [{"full_name": "Legacy CDS service"}],
        "publication_year": "2021",
        "document_type": "BOOK",
        "restricted": True,
        "notes": """This document is used whenever a document is required
        but it was not existing in the previous system...
        """,
    }

    return create_default_record(
        data,
        current_app_ils.document_record_cls,
        current_app_ils.document_indexer,
        DOCUMENT_PID_TYPE,
    )


def create_unknown_library():
    """Create migration library."""
    data = {
        "pid": MIGRATION_LIBRARY_PID,
        "name": "Migrated Unknown Library",
        "legacy_ids": ["0"],
        "notes": """This Library is used whenever we had library with
        legacy ID 0 in CDS Acquisition and ILL data.
        """,
    }

    return create_default_record(
        data,
        current_ils_ill.library_record_cls,
        current_ils_ill.library_indexer(),
        LIBRARY_PID_TYPE,
    )


def create_unknown_vendor():
    """Create migration vendor."""
    data = {
        "pid": MIGRATION_VENDOR_PID,
        "name": "Migrated Unknown Vendor",
        "legacy_ids": ["0"],
        "notes": """This Vendor is used whenever we had vendor ID 0
        in CDS Acquisition and ILL data.
        """,
    }

    return create_default_record(
        data,
        current_ils_acq.vendor_record_cls,
        current_ils_acq.vendor_indexer,
        VENDOR_PID_TYPE,
    )


def create_design_report():
    """Create Design report series."""
    data = {
        "pid": MIGRATION_DESIGN_PID,
        "title": "Design report",
        "mode_of_issuance": "SERIAL",
    }

    return create_default_record(
        data,
        current_app_ils.series_record_cls,
        current_app_ils.series_indexer,
        SERIES_PID_TYPE,
    )


def create_default_records():
    """Create migration records."""
    create_unknown_document()
    create_unknown_vendor()
    create_unknown_library()
    create_design_report()
