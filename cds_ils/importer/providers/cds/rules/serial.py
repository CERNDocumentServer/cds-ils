# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS MARCXML Serial rules."""

from dojson.utils import for_each_value

from ..models.serial import model
from .multipart import isbns as multipart_identifiers
from .utils import clean_val, filter_list_values, out_strip


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
    return clean_val("a", value, str, req=True)


@model.over("identifiers", "^020__")
@filter_list_values
def identifiers(self, key, value):
    """Translates identifiers fields."""
    return multipart_identifiers(self, key, value)
