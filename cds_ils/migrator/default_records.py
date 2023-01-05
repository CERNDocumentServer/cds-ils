# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator."""
import uuid

from invenio_app_ils.documents.api import DOCUMENT_PID_TYPE
from invenio_app_ils.items.api import ITEM_PID_TYPE
from invenio_app_ils.providers.api import PROVIDER_PID_TYPE
from invenio_app_ils.providers.proxies import current_ils_prov
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.series.api import SERIES_PID_TYPE
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from cds_ils.migrator.constants import (
    MIGRATION_DESIGN_PID,
    MIGRATION_DOCUMENT_PID,
    MIGRATION_ITEM_PID,
    MIGRATION_PROVIDER_PID,
)
from cds_ils.migrator.internal_locations.api import (
    get_internal_location_by_legacy_recid,
)


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


def create_unknown_provider():
    """Create migration provider."""
    data = {
        "pid": MIGRATION_PROVIDER_PID,
        "name": "Migrated Unknown Provider",
        "legacy_ids": ["0"],
        "type": "LIBRARY",
        "notes": "This provider is used whenever "
        "we had provider ID 0 in CDS Acquisition and ILL data.",
    }

    return create_default_record(
        data,
        current_ils_prov.provider_record_cls,
        current_ils_prov.provider_indexer,
        PROVIDER_PID_TYPE,
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


def create_unknown_item():
    """Create unknown item."""
    DEFAULT_INTERNAL_LOCATION_LEGACY_ID = 3
    int_loc_pid_value = get_internal_location_by_legacy_recid(
        DEFAULT_INTERNAL_LOCATION_LEGACY_ID
    ).pid.pid_value
    data = {
        "created_by": {"type": "script", "value": "migration"},
        "internal_location_pid": int_loc_pid_value,
        "barcode": "DEFAULT",
        "status": "FOR_REFERENCE_ONLY",
        "pid": MIGRATION_ITEM_PID,
        "document_pid": MIGRATION_DOCUMENT_PID,
        "circulation_restriction": "NO_RESTRICTION",
        "medium": "PAPER",
    }
    create_default_record(
        data,
        current_app_ils.item_record_cls,
        current_app_ils.item_indexer,
        ITEM_PID_TYPE,
    )


def create_default_records():
    """Create migration records."""
    create_unknown_document()
    create_unknown_provider()
    create_design_report()
