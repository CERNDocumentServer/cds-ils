# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.
"""CDS-ILS Standard model."""

from __future__ import unicode_literals

from copy import deepcopy

from cds_ils.importer.overdo import CdsIlsOverdo
from cds_ils.importer.providers.cds.cds import get_helper_dict
from cds_ils.importer.providers.cds.cds import model as base_model
from cds_ils.importer.providers.cds.ignore_fields import CDS_IGNORE_FIELDS


class CDSStandard(CdsIlsOverdo):
    """Translation Index for CDS Books."""

    __query__ = (
        "003:SzGeCERN 690C_:STANDARD OR 980__:STANDARD "
        "-980__:DELETED -980__:MIGRATED"
    )

    __ignore_keys__ = CDS_IGNORE_FIELDS

    _default_fields = {"_migration": {**get_helper_dict()}}

    def do(
        self,
        blob,
        ignore_missing=True,
        exception_handlers=None,
        init_fields=None,
    ):
        """Overwrite the do method."""
        init_fields = deepcopy(self._default_fields)
        return super().do(
            blob, ignore_missing, exception_handlers, init_fields
        )


model = CDSStandard(
    bases=(base_model,), entry_point_group="cds_ils.importer.cds.document"
)
