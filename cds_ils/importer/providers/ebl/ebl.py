# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS EBL Importer."""

from cds_ils.importer.base_model import Base
from cds_ils.importer.base_model import model as model_base
from cds_ils.importer.providers.ebl.ignore_fields import EBL_IGNORE_FIELDS


class EBLModel(Base):
    """EBL model class."""

    __query__ = "003:MiAaPQ"

    __ignore_keys__ = EBL_IGNORE_FIELDS

    _default_fields = {"document_type": "BOOK"}


model = EBLModel(
    bases=(model_base,), entry_point_group="cds_ils.importer.document"
)
