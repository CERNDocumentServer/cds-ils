# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS MARCXML Standard rules."""

from __future__ import unicode_literals

from dojson.errors import IgnoreKey
from dojson.utils import force_list
from invenio_app_ils.relations.api import OTHER_RELATION

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
        raise UnexpectedValue()

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
    _migration = self["_migration"]
    _related = _migration["related"]
    empty = not bool(_publication_info)
    for i, v in enumerate(force_list(value)):
        temp_info = {}
        pages = clean_val("k", v, str)
        if pages:
            temp_info.update(pages=pages)
        rel_recid = clean_val("b", v, str)
        if rel_recid:
            _related.append(
                {
                    "related_recid": rel_recid,
                    "relation_type": OTHER_RELATION.name,
                    "relation_description": "is chapter of"
                }
            )
            _migration.update({"related": _related, "has_related": True})
        if not empty and i < len(_publication_info):
            _publication_info[i].update(temp_info)
        else:
            _publication_info.append(temp_info)

    return _publication_info
