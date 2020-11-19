# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS EBL Importer."""

from cds_ils.importer.base_model import Base
from cds_ils.importer.base_model import model as model_base
from cds_ils.importer.providers.safari.ignore_fields import \
    SAFARI_IGNORE_FIELDS


class SafariModel(Base):
    """Safari model class."""

    __query__ = "003:CaSebORM"

    __ignore_keys__ = SAFARI_IGNORE_FIELDS

    _default_fields = {"document_type": "BOOK"}


model = SafariModel(
    bases=(model_base,), entry_point_group="cds_ils.importer.document"
)
