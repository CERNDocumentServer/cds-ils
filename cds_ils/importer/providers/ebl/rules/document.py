# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS EBL Importer dojson rules."""

import re

import pycountry
from dojson.utils import for_each_value, force_list

from cds_ils.importer.errors import UnexpectedValue
from cds_ils.importer.providers.cds.helpers.decorators import \
    filter_empty_dict_values, filter_list_values, out_strip
from cds_ils.importer.providers.cds.helpers.parsers import clean_val
from cds_ils.importer.providers.ebl.ebl import model

# REQUIRED_FIELDS


@model.over("alternative_identifiers", "^001")
@filter_list_values
def recid(self, key, value):
    """Record Identifier."""
    self["provider_recid"] = value
    return [{"scheme": "EBL", "value": value}]


@model.over("agency_code", "^003")
def agency_code(self, key, value):
    """Control number identifier."""
    return value


@model.over("authors", "(^1001_)|(^7001_)")
@filter_list_values
def authors(self, key, value):
    """Translates authors."""
    _authors = self.get("authors", [])

    author = {
        "full_name":
            clean_val("a", value, str, req=True).rstrip(".")
    }
    _authors.append(author)
    return _authors


@model.over("title", "^24510")
@out_strip
def title(self, key, value):
    """Translates title."""
    if "title" in self:
        raise UnexpectedValue()

    if "b" in value:
        _alternative_titles = self.get("alternative_titles", [])
        _alternative_titles.append(
            {
                "value": clean_val("b", value, str).rstrip('.'),
                "type": "SUBTITLE",
            }
        )
        self["alternative_titles"] = _alternative_titles
    return clean_val("a", value, str, req=True).rstrip('.')


# EITEM fields


@model.over("_eitem", "^85640")
@out_strip
def eitem(self, key, value):
    """Translate included eitems."""
    _eitem = self.get("_eitem", {})

    urls = []
    for v in force_list(value):
        urls.append(
            {
                "description": "E-book by EbookCentral",
                "value": clean_val("u", v, str),
            }
        )
    _eitem.update({"urls": urls})
    return _eitem


# OPTIONAL FIELDS

@model.over("identifiers", "^020__")
@filter_list_values
def identifiers(self, key, value):
    """Translate identifiers."""
    _identifiers = self.get("identifiers", [])
    if "a" in value:
        isbn = {
            "scheme": "ISBN",
            "value": clean_val("a", value, str, req=True),
            "material": "DIGITAL"
        }
        if isbn not in _identifiers:
            _identifiers.append(isbn)
    if "z" in value:
        isbn = {
            "scheme": "ISBN",
            "value": clean_val("z", value, str, req=True),
            "material": "PRINT_VERSION"
        }
        if isbn not in _identifiers:
            _identifiers.append(isbn)
    return _identifiers


@model.over("alternative_identifiers", "^035__")
@filter_list_values
def alternative_identifiers(self, key, value):
    """Translate alternative identifiers."""
    _alternative_identifiers = self.get("alternative_identifiers", [])

    if "a" in value:
        val_a = clean_val("a", value, str, req=True)
        if "(Au-PeEL)" in val_a:
            val_a = val_a.replace("(Au-PeEL)", "").replace("EBL", "")
            _alternative_identifiers.append({
                "scheme": "EBL",
                "value": val_a
            })
    return _alternative_identifiers


@model.over("languages", "^040__")
@for_each_value
@out_strip
def languages(self, key, value):
    """Translates languages fields."""
    lang = clean_val("b", value, str).lower()
    try:
        return pycountry.languages.lookup(lang).alpha_3.upper()
    except (KeyError, AttributeError, LookupError):
        raise UnexpectedValue(subfield="a")


@model.over("subjects", "^050_4")
@filter_list_values
def subjects_loc(self, key, value):
    """Translates subject classification."""
    _subjects = self.get("subjects", [])

    _subjects.append({"scheme": "LOC", "value": clean_val("a", value, str)})
    return _subjects


@model.over("subjects", "^0820_")
@filter_list_values
def subjects_dewey(self, key, value):
    """Translates subject classification."""
    _subjects = self.get("subjects", [])

    _subjects.append({"scheme": "DEWEY", "value": clean_val("a", value, str)})
    return _subjects


@model.over("edition", "^250__")
@out_strip
def edition(self, key, value):
    """Translate edition field."""
    return clean_val("a", value, str).replace("ed.", "").replace("edition", "")


@model.over("imprint", "^264_1")
@filter_empty_dict_values
def imprint(self, key, value):
    """Translate imprint field."""
    _publication_year = self.get("publication_year")
    if _publication_year:
        raise UnexpectedValue(subfield="e", message="doubled publication year")
    pub_year = clean_val("c", value, str).rstrip('.')
    self["publication_year"] = pub_year

    return {
        "place": clean_val("a", value, str).rstrip(':'),
        "publisher": clean_val("b", value, str).rstrip(','),
        "date": pub_year,
    }


@model.over("number_of_pages", "^300__")
@out_strip
def number_of_pages(self, key, value):
    """Translate number of pages."""
    numbers = re.findall(r"\d+", clean_val("a", value, str))
    return numbers[0]


@model.over("_serial", "^4901_")
@filter_list_values
@for_each_value
def serial(self, key, value):
    """Translate serial."""
    issn_value = clean_val("x", value, str)
    identifiers = None
    if issn_value:
        identifiers = [{"scheme": "ISSN", "value": issn_value}]

    volume = clean_val("v", value, str)
    if volume:
        volume = re.findall(r"\d+", volume)

    return {
        "title": clean_val("a", value, str, req=True),
        "identifiers": identifiers,
        "volume": volume[0] if volume else None,
    }


@model.over("table_of_content", "^5050_")
@out_strip
def table_of_content(self, key, value):
    """Translate table of content."""
    return clean_val("a", value, str).split("--")


@model.over("abstract", "^520__")
@out_strip
def abstract(self, key, value):
    """Translate abstract."""
    return clean_val("a", value, str)


@model.over("keywords", "^650_0")
@filter_list_values
def keywords(self, key, value):
    """Translate keywords."""
    _keywords = self.get("keywords", [])

    keyword = {"source": "EBL",
               "value": clean_val("a", value, str, req=True).rstrip(':')}

    if keyword not in _keywords:
        _keywords.append(keyword)
    return _keywords
