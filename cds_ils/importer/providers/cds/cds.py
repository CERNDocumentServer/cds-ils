# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS CDS Importer module."""
from copy import deepcopy

from cds_ils.importer.base_model import Base
from cds_ils.importer.base_model import model as model_base
from cds_ils.importer.providers.cds.ignore_fields import CDS_IGNORE_FIELDS


def get_helper_dict():
    """Return migration extra data."""
    _helper_dict = dict(
        record_type="document",
        volumes=[],
        serials=[],
        has_serial=False,
        is_multipart=False,
        has_tags=False,
        has_related=False,
        has_journal=False,
        tags=[],
        journal_record_legacy_id="",
        eitems_proxy=[],
        eitems_has_proxy=False,
        eitems_file_links=[],
        eitems_has_files=False,
        eitems_external=[],
        eitems_has_external=False,
        eitems_ebl=[],
        eitems_has_ebl=False,
        related=[],
    )

    return deepcopy(_helper_dict)


class CDSBase(Base):
    """Translation Index for CDS Books."""

    __query__ = "003:SzGeCERN -980:DELETED"

    __schema__ = "/schemas/documents/document-v1.0.0.json"

    __ignore_keys__ = CDS_IGNORE_FIELDS

    _default_fields = {"_migration": {**get_helper_dict()}}


model = CDSBase(
    bases=(model_base,), entry_point_group="cds_ils.importer.document"
)
