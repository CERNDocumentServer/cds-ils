# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS MARCXML Multipart rules."""

import re

from dojson.errors import IgnoreKey
from dojson.utils import for_each_value, force_list

from cds_ils.importer.errors import MissingRequiredField, UnexpectedValue

from ..models.multipart import model
from .base import book_series as base_book_series
from .utils import clean_val, extract_parts, extract_volume_info, \
    extract_volume_number, filter_list_values, out_strip


@model.over("legacy_recid", "^001")
def recid(self, key, value):
    """Record Identifier."""
    return int(value)


@model.over("identifiers", "^020__")
@filter_list_values
@for_each_value
def isbns(self, key, value):
    """Translates isbns stored in the record."""
    _migration = self.get("_migration", {"volumes": []})
    _identifiers = self.get("identifiers", [])

    val_u = clean_val("u", value, str)
    val_a = clean_val("a", value, str)
    val_b = clean_val("b", value, str)

    if val_u:
        volume_info = extract_volume_info(val_u)
        # if set found it means that the isbn is for the whole multipart
        set_search = re.search(r"(.*?)\(set\.*\)", val_u)
        if volume_info:
            # if we have volume there it means that the ISBN is of the volume
            volume_obj = {
                "volume": volume_info["volume"],
                "isbn": clean_val("a", value, str),
                "physical_description": volume_info["description"].strip(),
                "is_electronic": val_b is not None,
            }
            _migration["volumes"].append(volume_obj)
            self["_migration"] = _migration
            raise IgnoreKey("identifiers")
        if set_search:
            self["physical_description"] = set_search.group(1).strip()
            isbn = {"scheme": "ISBN", "value": val_a}
            return isbn if isbn not in _identifiers else None
        if not volume_info:
            # Try to find a volume number
            if extract_volume_number(val_u, search=True):
                raise UnexpectedValue(
                    subfield="u",
                    message=" found volume but failed to parse description",
                )
            else:
                self["physical_description"] = val_u
                isbn = {"scheme": "ISBN", "value": val_a}
                return isbn if isbn not in _identifiers else None
        if not set_search and not volume_info:
            self["physical_description"] = val_u
            isbn = {"scheme": "ISBN", "value": val_a}
            return isbn if isbn not in _identifiers else None
    elif not val_u and val_a:
        # if I dont have volume info but only isbn
        isbn = {"scheme": "ISBN", "value": val_a}
        return isbn if isbn not in _identifiers else None
    else:
        raise UnexpectedValue(subfield="a", message=" isbn not provided")


@model.over("title", "^245__")
@out_strip
def title(self, key, value):
    """Translates book series title."""
    # assume that is goes by order of fields and check 245 first
    if "b" in value:
        _alternative_titles = self.get("alternative_titles", [])
        _alternative_titles.append(
            {"type": "SUBTITLE", "value": clean_val("b", value, str)}
        )
        self["alternative_titles"] = _alternative_titles
    return clean_val("a", value, str)


@model.over("_migration", "^246__")
def migration(self, key, value):
    """Translates volumes titles."""
    _series_title = self.get("title", None)

    # I added this in the model, I'm sure it's there
    _migration = self.get("_migration", {})
    if "volumes" not in _migration:
        _migration["volumes"] = []

    for v in force_list(value):
        # check if it is a multipart monograph
        val_n = clean_val("n", v, str)
        val_p = clean_val("p", v, str)
        if not val_n and not val_p:
            raise UnexpectedValue(
                subfield="n", message=" this record is probably not a series"
            )
        if val_p and not val_n:
            raise UnexpectedValue(
                subfield="n",
                message=" volume title exists but no volume number",
            )

        if val_p and extract_volume_number(val_p, search=True):
            # Some records have the volume number in p
            raise UnexpectedValue(
                subfield="p", message=" found volume number in the title"
            )

        volume_index = re.findall(r"\d+", val_n) if val_n else None
        if volume_index and len(volume_index) > 1:
            raise UnexpectedValue(
                subfield="n", message=" volume has more than one digit "
            )
        else:
            volume_number = extract_volume_number(
                val_n, raise_exception=True, subfield="n"
            )
            volume_obj = {
                "title": val_p,
                "volume": volume_number,
            }
            _migration["volumes"].append(volume_obj)
    if not _series_title:
        raise MissingRequiredField(
            subfield="a", message=" this record is missing a main title"
        )

    # series created

    return _migration


@model.over("number_of_volumes", "^300__")
@out_strip
def number_of_volumes(self, key, value):
    """Translates number of volumes."""
    _series_title = self.get("title", None)
    if not _series_title:
        raise MissingRequiredField(
            subfield="a", message=" this record is missing a main title"
        )
    val_a = clean_val("a", value, str)
    parsed_a = extract_parts(val_a)
    if not parsed_a["number_of_pages"] and ("v" in val_a or "vol" in val_a):
        _volumes = re.findall(r"\d+", val_a)
        if _volumes:
            return _volumes[0]
    raise IgnoreKey("number_of_volumes")


@model.over("book_series", "^490__")
@for_each_value
def book_series(self, key, value):
    """Match barcodes to volumes."""
    base_book_series(self, key, value)
