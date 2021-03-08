# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS MARCXML Journal rules."""

from dojson.errors import IgnoreKey
from dojson.utils import for_each_value, force_list
from invenio_app_ils.relations.api import LANGUAGE_RELATION, OTHER_RELATION, \
    SEQUENCE_RELATION

from cds_ils.importer.errors import ManualImportRequired, UnexpectedValue
from cds_ils.importer.providers.cds.models.journal import model

from .base import title as base_title
from .utils import clean_val, filter_list_values, out_strip
from .values_mapping import ACCESS_TYPE, COLLECTION, DOCUMENT_TYPE, MEDIUMS, \
    mapping


@model.over("legacy_recid", "^001", override=True)
def recid(self, key, value):
    """Record Identifier."""
    self["mode_of_issuance"] = "SERIAL"
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


@model.over("alternative_titles", "^210__")
@filter_list_values
def abbreviated_title(self, key, value):
    """Translates abbreviated title field."""
    _alternative_titles = self.get("alternative_titles", [])
    sub_a = clean_val("a", value, str, req=True)
    _alternative_titles.append({"type": "ABBREVIATION", 'value': sub_a})
    return _alternative_titles


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


@model.over("note", "(^935__)")
@out_strip
def note(self, key, value):
    """Translates note field."""
    notes_list = [self.get("note", "")]
    notes_list.append(clean_val("a", value, str))

    return " \n".join(filter(None, notes_list))


@model.over("publisher", "^933__")
@out_strip
def publisher(self, key, value):
    """Translates publisher field."""
    return clean_val("b", value, str, req=True)


@model.over("electronic_volumes_description", "(^362__)")
def electronic_volumes_description(self, key, value):
    """Translates electronic volumes description field."""
    return clean_val("a", value, str, req=True)


@model.over("physical_volumes", "(^866__)")
@filter_list_values
def physical_volumes(self, key, value):
    """Translates physical volumes description field."""
    _physical_volumes = self.get("physical_volumes", [])
    physical_volumes_dict = {
        "description": clean_val("a", value, str),
        "location": clean_val("b", value, str),
    }
    _physical_volumes.append(physical_volumes_dict)

    return _physical_volumes


@model.over("access_urls", "^85641")
@filter_list_values
def access_urls(self, key, value):
    """Translates access urls field."""
    _access_urls = self.get("access_urls", [])
    access_type_mapped = []
    val_x = clean_val("x", value, str)
    access_type_list = list(map(int, val_x if val_x else []))
    for i in access_type_list:
        access_type = mapping(ACCESS_TYPE, str(i), raise_exception=True)
        access_type_mapped.append(access_type)
    url_dict = {
        "value": clean_val("u", value, str, req=True),
        "description": clean_val("z", value, str),
        "access_restriction": access_type_mapped,
    }
    _access_urls.append(url_dict)

    url_note = clean_val("3", value, str)
    if url_note:
        notes = self.get("note", "")
        notes_list = [notes, url_note]
        self["note"] = " \n".join(filter(None, notes_list))

    return _access_urls


@model.over("urls", "^85642")
@filter_list_values
def urls(self, key, value):
    """Translates urls field."""
    _urls = self.get("urls", [])

    url_dict = {
        "value": clean_val("u", value, str),
        "description": clean_val("y", value, str),
    }
    _urls.append(url_dict)

    return _urls


@model.over(
    "_migration", "(^770__)|(^772__)|(^780__)|(^785__)|(^787__)", override=True
)
def related_records(self, key, value):
    """Translates related_records field."""
    _migration = self.get("_migration", {})
    _related = _migration.get("related", [])
    description = None
    relation_type = OTHER_RELATION.name

    # language
    if key == "787__":
        if "i" in value:
            relation_language = clean_val("i", value, str)
            if relation_language:
                relation_type = LANGUAGE_RELATION.name

    # has supplement/supplement to
    if key == "770__" or key == "772__":
        if "i" in value:
            description = clean_val("i", value, str)

    # continues/is continued by
    if key == "780__" or key == "785__":
        if "i" in value:
            relation_sequence = clean_val("i", value, str)
            if relation_sequence:
                relation_type = SEQUENCE_RELATION.name
                if key == "780__":
                    sequence_order = "next"
                else:
                    sequence_order = "previous"

    related_dict = {
        "related_recid": clean_val("w", value, str, req=True),
        "relation_type": relation_type,
        "relation_description": description,
    }
    if relation_type == SEQUENCE_RELATION.name:
        related_dict.update({"sequence_order": sequence_order})

    _related.append(related_dict)

    _migration.update(
        {
            "related": _related,
            "has_related": True,
        }
    )

    return _migration


@model.over("_migration", "^340__")
@out_strip
def medium(self, key, value):
    """Translates medium."""
    _migration = self.get("_migration", {})
    item_mediums = _migration.get("item_medium", [])
    barcodes = force_list(value.get("x", ""))
    _medium = mapping(MEDIUMS,
                      clean_val("a", value, str).upper().replace('-', ''),
                      raise_exception=True)

    for barcode in barcodes:
        current_item = {
            "barcode": barcode,
            "medium": _medium,
        }
        if current_item not in item_mediums:
            item_mediums.append(current_item)
    _migration.update(
        {
            "item_medium": item_mediums,
            "has_medium": True,
        }
    )
    return _migration


@model.over("tags", "(^980__)|(^690C_)", override=True)
@out_strip
def tags(self, key, value):
    """Translates tag field - WARNING - also document type and serial field."""
    _tags = self.get("tags", [])
    for v in force_list(value):
        result_a = mapping(COLLECTION, clean_val("a", v, str))
        result_b = mapping(COLLECTION, clean_val("b", v, str))
        if result_a:
            _tags.append(result_a) if result_a not in _tags else None
        if result_b:
            _tags.append(result_b) if result_b not in _tags else None
        if not result_a and not result_b:
            document_type(self, key, value)
    return _tags


@model.over("document_type", "(^980__)|(^960__)|(^690C_)", override=True)
@out_strip
def document_type(self, key, value):
    """Translates document type field."""
    for v in force_list(value):
        clean_val_a = clean_val("a", v, str)
        if ((key == "980__" or key == "690C_") and clean_val_a == "PERI") \
                or key == "960__" and clean_val_a == "31":
            raise IgnoreKey("document_type")
        else:
            raise UnexpectedValue(subfield="a")
