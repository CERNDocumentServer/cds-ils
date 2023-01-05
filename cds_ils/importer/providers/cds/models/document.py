# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Book model."""

from __future__ import unicode_literals

from copy import deepcopy

from cds_ils.importer.overdo import CdsIlsOverdo
from cds_ils.importer.providers.cds.cds import get_helper_dict
from cds_ils.importer.providers.cds.cds import model as base_model
from cds_ils.importer.providers.cds.ignore_fields import CDS_IGNORE_FIELDS


class CDSDocument(CdsIlsOverdo):
    """Translation Index for CDS Books."""

    __query__ = (
        "003:SzGeCERN 690C_:BOOK OR 690C_:CONFERENCE OR "
        '690C_:"YELLOW REPORT" OR '
        "980__:PROCEEDINGS OR "
        "(-980:STANDARD 980:BOOK) OR "
        "697C_:LEGSERLIB AND "
        "(-980__:STANDARD "
        "-596__:MULTIVOLUMES1 -596__:MULTIVOLUMESX)"
    )

    __model_ignore_keys__ = {
        # this field is used to match multipart monograph items as volumes
        "020__b",
        "0247_9",
        "084__2",
        "084__a",
        "270__b",
        "540__u",
        "700__i",
        "710__5",
        "700__m",
        "100__m",
        "775__n",
        "775__p",
    }

    __ignore_keys__ = CDS_IGNORE_FIELDS | __model_ignore_keys__

    _default_fields = {"_migration": {**get_helper_dict(record_type="document")}}

    rectype = "document"

    def do(
        self,
        blob,
        ignore_missing=True,
        exception_handlers=None,
        init_fields=None,
    ):
        """Overwrite the do method."""
        init_fields = deepcopy(self._default_fields)
        return super().do(blob, ignore_missing, exception_handlers, init_fields)


model = CDSDocument(
    bases=(base_model,), entry_point_group="cds_ils.importer.cds.document"
)
