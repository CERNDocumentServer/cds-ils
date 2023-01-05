# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Series model."""

from __future__ import unicode_literals

from copy import deepcopy

from cds_ils.importer.overdo import CdsIlsOverdo
from cds_ils.importer.providers.cds.ignore_fields import CDS_IGNORE_FIELDS

from ..cds import get_helper_dict
from ..cds import model as cds_base
from .document import model as books_base


class CDSMultipart(CdsIlsOverdo):
    """Translation Index for CDS Books."""

    __query__ = "596__:MULTIVOLUMES -980__:DELETED -980__:MIGRATED"

    __ignore_keys__ = CDS_IGNORE_FIELDS | {
        "084__c",
        "084__b",
    }

    _default_fields = {
        "_migration": {**get_helper_dict(record_type="document")},
        "mode_of_issuance": "MULTIPART_MONOGRAPH",
    }
    rectype = "multipart"

    def do(
        self,
        blob,
        ignore_missing=True,
        exception_handlers=None,
        init_fields=None,
    ):
        """Overwrite the do method."""
        self._default_fields["_migration"]["record_type"] = "multipart"
        init_fields = deepcopy(self._default_fields)
        return super().do(blob, ignore_missing, exception_handlers, init_fields)


model = CDSMultipart(
    bases=(
        cds_base,
        books_base,
    ),
    entry_point_group="cds_ils.importer.series",
)
