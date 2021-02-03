# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS MARCXML book rules."""

from __future__ import absolute_import, print_function, unicode_literals

from cds_ils.importer.providers.cds.models.book import model

from .base import alternative_titles as alternative_titles_base
from .utils import clean_val, filter_list_values


@model.over("alternative_titles", "(^246__)|(^242__)")
@filter_list_values
def alternative_titles(self, key, value):
    """Alternative titles."""
    _alternative_titles = self.get("alternative_titles", [])

    if key == "242__":
        _alternative_titles += alternative_titles_base(self, key, value)
    elif key == "246__":
        if "a" in value:
            _alternative_titles.append(
                {
                    "value": clean_val("a", value, str, req=True),
                    "type": "ALTERNATIVE_TITLE",
                }
            )
        if "b" in value:
            _alternative_titles.append(
                {
                    "value": clean_val("b", value, str, req=True),
                    "type": "SUBTITLE",
                }
            )
        return _alternative_titles
