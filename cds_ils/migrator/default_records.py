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
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

MIGRATION_DOCUMENT_PID = "DOCPID-44444"
MIGRATION_LIBRARY_PID = "LIBPID-44444"
MIGRATION_VENDOR_PID = "VENPID-44444"


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
    record_uuid = mint_migration_records(DOCUMENT_PID_TYPE, "pid", data)
    doc = current_app_ils.document_record_cls.create(data, record_uuid)
    db.session.commit()
    current_app_ils.document_indexer.index(doc)
    return doc


def create_unknown_library():
    """Create migration library."""
    data = {
        "pid": MIGRATION_LIBRARY_PID,
        "name": "Migrated Unknown Library",
        "legacy_id": "0",
        "notes": """This Library is used whenever we had library with
        legacy ID 0 in CDS Acquisition and ILL data.
        """,
    }

    record_uuid = mint_migration_records(LIBRARY_PID_TYPE, "pid", data)
    library = current_ils_ill.library_record_cls.create(data, record_uuid)
    db.session.commit()
    current_ils_ill.library_indexer().index(library)
    return library


def create_unknown_vendor():
    """Create migration vendor."""
    data = {
        "pid": MIGRATION_VENDOR_PID,
        "name": "Migrated Unknown Vendor",
        "legacy_id": "0",
        "notes": """This Vendor is used whenever we had vendor ID 0
        in CDS Acquisition and ILL data.
        """,
    }

    record_uuid = mint_migration_records(VENDOR_PID_TYPE, "pid", data)
    vendor = current_ils_acq.vendor_record_cls.create(data, record_uuid)
    db.session.commit()
    current_ils_acq.vendor_indexer.index(vendor)
    return vendor


def create_unknown_records():
    """Create migration records."""
    create_unknown_document()
    create_unknown_vendor()
    create_unknown_library()
