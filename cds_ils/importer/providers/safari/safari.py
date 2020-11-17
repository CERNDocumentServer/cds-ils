# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS EBL Importer."""

from cds_ils.importer.base import Base
from cds_ils.importer.base import model as model_base
from cds_ils.importer.providers.safari.ignore_fields import \
    SAFARI_IGNORE_FIELDS


class SafariModel(Base):
    """Safari model class."""

    __query__ = "003:CaSebORM"

    __ignore_keys__ = SAFARI_IGNORE_FIELDS

    _defaults = {"document_type": "BOOK"}

    def do(
        self,
        blob,
        ignore_missing=True,
        exception_handlers=None,
        init_fields=None,
    ):
        """Set schema after translation depending on the model."""
        json = {}
        # set default values
        json.update(self._defaults)

        # import fields from xml
        json.update(
            super(SafariModel, self).do(
                blob=blob,
                ignore_missing=ignore_missing,
                exception_handlers=exception_handlers,
            )
        )

        return json


model = SafariModel(
    bases=(model_base,), entry_point_group="cds_ils.marc21.document"
)
