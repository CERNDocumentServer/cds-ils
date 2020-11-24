# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS MARCXML Journal rules."""


import pycountry
from dojson.utils import for_each_value

from cds_ils.importer.errors import UnexpectedValue
from cds_ils.importer.providers.cds.models.journal import model

from .book import title as base_title
from .utils import clean_val, filter_list_values, out_strip


@model.over("legacy_recid", "^001")
def recid(self, key, value):
    """Record Identifier."""
    return int(value)


@model.over("title", "^245__")
@out_strip
def title(self, key, value):
    """Translates title."""
    return base_title(self, key, value)


@model.over("alternative_titles", "^246_3")
@filter_list_values
def alternative_titles_journal(self, key, value):
    """Translates alternative titles."""
    _alternative_titles = self.get("alternative_titles", [])

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


@model.over("abbreviated_title", "^210__")
@out_strip
def abbreviated_title(self, key, value):
    """Translates abbreviated title field."""
    return clean_val("a", value, str, req=True)


@model.over("identifiers", "^022__")
@filter_list_values
@for_each_value
def identifiers(self, key, value):
    """Translates identifiers fields."""
    val_a = clean_val("a", value, str, req=True)
    return {
        "scheme": "ISSN",
        "value": val_a,
        "material": clean_val("b", value, str),
    }


@model.over("internal_notes", "^937__")
@for_each_value
@out_strip
def internal_notes(self, key, value):
    """Translates internal notes field."""
    return {"value": clean_val("a", value, str, req=True)}


@model.over("note", "^935__")
@out_strip
def note(self, key, value):
    """Translates note field."""
    return clean_val("a", value, str, req=True)


@model.over("publisher", "^933__")
@out_strip
def publisher(self, key, value):
    """Translates publisher field."""
    return clean_val("b", value, str, req=True)


@model.over("languages", "^041__")
@for_each_value
@out_strip
def languages(self, key, value):
    """Translates languages fields."""
    lang = clean_val("a", value, str).lower()
    try:
        return pycountry.languages.lookup(lang).alpha_2.upper()
    except (KeyError, AttributeError, LookupError):
        raise UnexpectedValue(subfield="a")


@model.over("_migration", "(^362__)|(^85641)|(^866__)|(^780__)|(^785__)")
def migration(self, key, value):
    """Translates fields related to children record types."""
    _migration = self.get("_migration", {})
    _electronic_items = _migration.get("electronic_items", [])
    _items = _migration.get("items", [])
    _relation_previous = _migration.get("relation_previous")
    _relation_next = _migration.get("relation_next")
    if key == "362__":
        _electronic_items.append({"subscription": clean_val("a", value, str)})
    if key == "85641":
        _electronic_items.append(
            {
                "subscription": clean_val("3", value, str),
                "url": clean_val("u", value, str),
                "access_type": clean_val("x", value, str),
                "note": clean_val("z", value, str),
            }
        )
    if key == "866__":
        _items.append(
            {
                "subscription": clean_val("a", value, str),
            }
        )
    if key == "780__":
        _relation_previous = clean_val("w", value, str, req=True)

    if key == "785__":
        _relation_next = clean_val("w", value, str, req=True)

    _migration.update(
        {
            "electronic_items": _electronic_items,
            "items": _items,
            "relation_previous": _relation_previous,
            "relation_next": _relation_next,
        }
    )
    return _migration
