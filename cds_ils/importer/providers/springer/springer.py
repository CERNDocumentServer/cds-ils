# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Springer model."""

from cds_ils.importer.base_model import Base
from cds_ils.importer.base_model import model as model_base
from cds_ils.importer.providers.springer.ignore_fields import \
    SPRINGER_IGNORE_FIELDS


class SpringerDocument(Base):
    """Springer model for XML mapping."""

    __query__ = "003:DE-He213"

    __ignore_keys__ = SPRINGER_IGNORE_FIELDS

    _default_fields = {"document_type": "BOOK"}


model = SpringerDocument(
    bases=(model_base,), entry_point_group="cds_ils.importer.document"
)
