# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS MARCXML Standard rules."""

from __future__ import unicode_literals

from dojson.errors import IgnoreKey
from dojson.utils import for_each_value, force_list
from flask import current_app

from cds_ils.importer.errors import UnexpectedValue
from cds_ils.importer.providers.cds.helpers.decorators import (
    filter_list_values,
    out_strip,
)
from cds_ils.importer.providers.cds.helpers.parsers import (
    clean_val,
    extract_parts,
    is_excluded,
)
from cds_ils.importer.providers.cds.models.standard import model


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
                "language": "FRA",
            }
        )
    if "b" in value:
        _alternative_titles.append(
            {
                "value": clean_val("b", value, str, req=True),
                "type": "TRANSLATED_SUBTITLE",
                "language": "FRA",
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
    if parts["physical_description"]:
        self["physical_description"] = parts["physical_description"]
    if parts["number_of_pages"]:
        return parts["number_of_pages"]
    raise UnexpectedValue(subfield="a")


@model.over("title", "^245__")
@out_strip
def title(self, key, value):
    """Translates title."""
    if "title" in self:
        raise UnexpectedValue(message="Ambiguous title")

    if "b" in value:
        _alternative_titles = self.get("alternative_titles", [])
        _alternative_titles.append(
            {"value": clean_val("b", value, str), "type": "SUBTITLE"}
        )
        self["alternative_titles"] = _alternative_titles
    return clean_val("a", value, str, req=True)


@model.over("publication_info", "^962__")
def publication_additional(self, key, value):
    """Translates additional publication info & other related_records field."""
    _publication_info = self.get("publication_info", [])
    _urls = self.get("urls", [])
    empty = not bool(_publication_info)
    host = current_app.config["SPA_HOST"]
    for i, v in enumerate(force_list(value)):
        temp_info = {}
        pages = clean_val("k", v, str)
        if pages:
            temp_info.update(pages=pages)
        related_recid = clean_val("b", v, str)
        if related_recid:
            _urls.append(
                {
                    "value": f"{host}/legacy/{related_recid}",
                    "description": "is chapter of",
                }
            )
        if not empty and i < len(_publication_info):
            _publication_info[i].update(temp_info)
        else:
            _publication_info.append(temp_info)
    self["urls"] = _urls
    return _publication_info


@model.over("subjects", "^084__")
@for_each_value
@out_strip
def subject_classification(self, key, value):
    """Translates subject classification field."""
    prev_subjects = self.get("subjects", [])
    _subject_classification = {
        "value": clean_val("c", value, str, req=True),
        "scheme": "ICS",
    }
    if _subject_classification not in prev_subjects:
        return _subject_classification
    else:
        raise IgnoreKey("subjects")
