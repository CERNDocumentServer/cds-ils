# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS EBL Importer."""
from copy import deepcopy

from cds_ils.importer.base_model import Base
from cds_ils.importer.base_model import model as model_base
from cds_ils.importer.providers.ebl.ignore_fields import EBL_IGNORE_FIELDS


class EBLModel(Base):
    """EBL model class."""

    __query__ = "003:MiAaPQ"

    __ignore_keys__ = EBL_IGNORE_FIELDS

    _default_fields = {"document_type": "BOOK", "languages": ["ENG"]}

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


model = EBLModel(bases=(model_base,), entry_point_group="cds_ils.importer.document")
