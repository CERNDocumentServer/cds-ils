# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS MARCXML Standard rules."""

from __future__ import unicode_literals

from dojson.errors import IgnoreKey

from cds_ils.importer.errors import UnexpectedValue
from cds_ils.importer.providers.cds.models.standard import model
from cds_ils.importer.providers.cds.rules.utils import clean_val, \
    extract_parts, filter_list_values, is_excluded, out_strip


@model.over("alternative_titles", "^246__", override=True)
@filter_list_values
def title_translations(self, key, value):
    """Translates title translations."""
    _alternative_titles = self.get("alternative_titles", [])

    if "a" in value:
        _alternative_titles.append(
            {
                "value": clean_val("a", value, str, req=True),
                "type": "TRANSLATED_TITLE",
                "language": "fr",
            }
        )
    if "b" in value:
        _alternative_titles.append(
            {
                "value": clean_val("b", value, str, req=True),
                "type": "TRANSLATED_SUBTITLE",
                "language": "fr",
            }
        )
    return _alternative_titles


@model.over("number_of_pages", "^300__")  # item
def number_of_pages(self, key, value):
    """Translates number_of_pages fields."""
    val = clean_val("a", value, str)
    if is_excluded(val):
        raise IgnoreKey("number_of_pages")

    parts = extract_parts(val)
    if parts["has_extra"]:
        raise UnexpectedValue(subfield="a")
    if parts["physical_copy_description"]:
        self["physical_copy_description"] = parts["physical_copy_description"]
    if parts["number_of_pages"]:
        return parts["number_of_pages"]
    raise UnexpectedValue(subfield="a")


@model.over("title", "^245__")
@out_strip
def title(self, key, value):
    """Translates title."""
    if "title" in self:
        raise UnexpectedValue()

    if "b" in value:
        _alternative_titles = self.get("alternative_titles", [])
        _alternative_titles.append(
            {"value": clean_val("b", value, str), "type": "SUBTITLE"}
        )
        self["alternative_titles"] = _alternative_titles
    return clean_val("a", value, str, req=True)
