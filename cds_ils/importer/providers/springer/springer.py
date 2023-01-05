# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Springer model."""
from copy import deepcopy

from cds_ils.importer.base_model import Base
from cds_ils.importer.base_model import model as model_base
from cds_ils.importer.providers.springer.ignore_fields import SPRINGER_IGNORE_FIELDS


class SpringerDocument(Base):
    """Springer model for XML mapping."""

    __query__ = "003:DE-He213"

    __ignore_keys__ = SPRINGER_IGNORE_FIELDS

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


model = SpringerDocument(
    bases=(model_base,), entry_point_group="cds_ils.importer.document"
)
