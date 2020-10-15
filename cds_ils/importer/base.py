# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer base module."""
from cds_dojson.marc21.models.books.base import CDSOverdoBookBase


class Base(CDSOverdoBookBase):
    """Base model conversion MARC21 to JSON."""


model = Base(entry_point_group="cds_dojson.marc21.base")
