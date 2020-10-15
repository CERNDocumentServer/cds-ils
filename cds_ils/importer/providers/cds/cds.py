# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS CDS Importer module."""

from cds_ils.importer.base import Base
from cds_ils.importer.base import model as model_base
from cds_ils.importer.providers.cds.ignore_fields import CDS_IGNORE_FIELDS


class CDSDocument(Base):
    """Translation Index for CDS Books."""

    __query__ = "003:SzGeCERN -980:DELETED"

    __schema__ = "/schemas/documents/document-v1.0.0.json"

    __ignore_keys__ = CDS_IGNORE_FIELDS

    def do(
        self,
        blob,
        ignore_missing=True,
        exception_handlers=None,
        init_fields=None,
    ):
        """Set schema after translation depending on the model."""
        json = super(CDSDocument, self).do(
            blob=blob,
            ignore_missing=ignore_missing,
            exception_handlers=exception_handlers,
        )

        json["$schema"] = self.__class__.__schema__

        return json


model = CDSDocument(
    bases=(model_base,), entry_point_group="cds_ils.marc21.document"
)
