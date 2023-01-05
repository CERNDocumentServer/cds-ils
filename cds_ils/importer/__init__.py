# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-IlS Importer module."""

from cds_dojson.matcher import matcher
from cds_dojson.overdo import OverdoBase
from dojson.contrib.marc21 import model as default_model


class CDSOverdoBase(OverdoBase):
    """Override of OverdoBase."""

    def do(self, blob, **kwargs):
        """Translate blob values and instantiate new model instance."""
        from .errors import RecordModelMissing

        model = matcher(blob, self.entry_point_models)

        if model == default_model:
            raise RecordModelMissing
        return matcher(blob, self.entry_point_models).do(blob, **kwargs)


marc21 = CDSOverdoBase(entry_point_models="cds_ils.importer.models")
