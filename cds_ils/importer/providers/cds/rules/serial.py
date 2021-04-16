# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS MARCXML Serial rules."""

from dojson.utils import for_each_value

from ..helpers.decorators import filter_list_values, out_strip
from ..helpers.parsers import clean_val
from ..models.serial import model
from .multipart import isbns as multipart_identifiers


@model.over("legacy_recid", "^001")
def recid(self, key, value):
    """Record Identifier."""
    return int(value)


@model.over("title", "^490__")
@for_each_value
@out_strip
def title(self, key, value):
    """Translates book series title."""
    _identifiers = self.get("identifiers", [])
    issn = clean_val("x", value, str)
    if issn:
        _identifiers.append({"scheme": "ISSN", "value": issn})
        self["identifiers"] = _identifiers
    self["mode_of_issuance"] = "SERIAL"
    _title = clean_val("a", value, str, req=True)
    return _title
