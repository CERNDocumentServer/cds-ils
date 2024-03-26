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
from cds_ils.importer.providers.safari.ignore_fields import SAFARI_IGNORE_FIELDS


class SafariModel(Base):
    """Safari model class."""

    __query__ = "003:OCoLC"

    __ignore_keys__ = SAFARI_IGNORE_FIELDS

    _default_fields = {"document_type": "BOOK"}

    @staticmethod
    def _add_missing_fields(document):
        """Adds missing fields.

        Adds necessary fields when missing after the transformation.
        """
        # Cannot be set before the transformation, otherwise ENG will be always there,
        # even if another language is already defined (languages are appended).
        document.setdefault("languages", ["ENG"])
        return document

    def do(
        self,
        blob,
        ignore_missing=True,
        exception_handlers=None,
        init_fields=None,
    ):
        """Overwrite the do method."""
        fields = deepcopy(self._default_fields)
        if init_fields:
            fields.update(init_fields)
        mapped = super().do(blob, ignore_missing, exception_handlers, fields)
        return self._add_missing_fields(mapped)


model = SafariModel(bases=(model_base,), entry_point_group="cds_ils.importer.document")
