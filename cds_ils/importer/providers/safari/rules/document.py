# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Safari Importer dojson rules."""

import re

import pycountry
from dojson.utils import for_each_value, force_list

from cds_ils.importer.errors import UnexpectedValue
from cds_ils.importer.providers.cds.rules.utils import clean_val, \
    filter_list_values, out_strip
from cds_ils.importer.providers.safari.safari import model
from cds_ils.importer.providers.utils import \
    _get_correct_ils_contributor_role, reverse_replace


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
        "full_name": clean_val("a", value, str, req=True),
        "roles": [
            _get_correct_ils_contributor_role("e", clean_val("e", value, str))
        ],
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
                "value": reverse_replace(clean_val("b", value, str), ".", ""),
                "type": "SUBTITLE",
            }
        )
        self["alternative_titles"] = _alternative_titles
    return reverse_replace(clean_val("a", value, str, req=True), ".", "")


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
                "description": "E-book by Safari",
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
    isbn = {
        "scheme": "ISBN",
        "value": clean_val("z", value, str, req=True),
    }
    if isbn not in _identifiers:
        _identifiers.append(isbn)
    return _identifiers


@model.over("languages", "^0410_")
@for_each_value
@out_strip
def languages(self, key, value):
    """Translates languages fields."""
    lang = clean_val("a", value, str).lower()
    try:
        return pycountry.languages.lookup(lang).alpha_2
    except (KeyError, AttributeError, LookupError):
        raise UnexpectedValue(subfield="a")


@model.over("edition", "^250__")
@out_strip
def edition(self, key, value):
    """Translate edition field."""
    return clean_val("a", value, str)


@model.over("imprint", "^264_1")
@out_strip
def imprint(self, key, value):
    """Translate imprint field."""
    _publication_year = self.get("publication_year")
    if _publication_year:
        raise UnexpectedValue(subfield="e", message="doubled publication year")
    pub_year = reverse_replace(clean_val("c", value, str), ".", "")
    self["publication_year"] = pub_year

    return {
        "publisher": reverse_replace(clean_val("b", value, str), ",", ""),
        "date": pub_year,
    }


@model.over("number_of_pages", "^300__")
@out_strip
def number_of_pages(self, key, value):
    """Translate number of pages."""
    numbers = re.findall(r"\d+", clean_val("a", value, str))
    return numbers[0]


@model.over("abstract", "^520__")
@out_strip
def abstract(self, key, value):
    """Translate abstract."""
    return clean_val("a", value, str)


@model.over("copyrights", "^542__")
@filter_list_values
@for_each_value
def copyrights(self, key, value):
    """Translate copyrights."""
    return {
        "year": clean_val("g", value, int),
        "statement": clean_val("f", value, str),
    }
