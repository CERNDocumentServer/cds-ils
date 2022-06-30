# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Safari Importer dojson rules."""

import re
import string

import pycountry
from dojson.utils import for_each_value, force_list

from cds_ils.importer.errors import UnexpectedValue
from cds_ils.importer.providers.cds.helpers.decorators import \
    filter_list_values, out_strip
from cds_ils.importer.providers.cds.helpers.parsers import clean_val
from cds_ils.importer.providers.cds.rules.values_mapping import EDITIONS, \
    IDENTIFIERS_MEDIUM_TYPES, mapping
from cds_ils.importer.providers.safari.safari import model
from cds_ils.importer.providers.utils import \
    _get_correct_ils_contributor_role, rreplace


@model.over("alternative_identifiers", "^001")
@filter_list_values
def recid(self, key, value):
    """Record Identifier."""
    self["provider_recid"] = value
    return [{"scheme": "SAFARI", "value": value}]


@model.over("agency_code", "^003")
def agency_code(self, key, value):
    """Control number identifier."""
    return value


@model.over("authors", "(^1001)|(^7001)")
@filter_list_values
def authors(self, key, value):
    """Translates authors."""
    _authors = self.get("authors", [])

    author = {
        "full_name": clean_val("a", value, str, req=True).strip(
            string.punctuation + string.whitespace
        ),
        "roles": [
            _get_correct_ils_contributor_role("e", clean_val("e", value, str))
        ],
        "type": "PERSON",
    }
    _authors.append(author)
    return _authors


@model.over("title", "^2451")
@out_strip
def title(self, key, value):
    """Translates title."""
    if "title" in self:
        raise UnexpectedValue(message="Ambiguous title")

    if "b" in value:
        _alternative_titles = self.get("alternative_titles", [])
        _alternative_titles.append(
            {
                "value": clean_val("b", value, str).strip(
                    string.punctuation + string.whitespace
                ),
                "type": "SUBTITLE",
            }
        )
        self["alternative_titles"] = _alternative_titles

    title = clean_val("a", value, str, req=True).strip(
        string.punctuation + string.whitespace
    )
    return title


@model.over("alternative_titles", "^246__")
@filter_list_values
def alternative_titles_doc(self, key, value):
    """Alternative titles."""
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
                "description": "e-book",
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

    def get_identifier(subfield):
        val = clean_val(subfield, value, str)
        if not val:
            return None

        only_digits = re.findall(r"\d+", val)
        if only_digits:
            val = only_digits[0]

        material = "PRINT_VERSION"
        _qs = clean_val("q", value, str, multiple_values=True)
        if _qs:
            # get only the first when multiple
            if len(force_list(_qs)) > 1:
                _qs = _qs[0]

            val_q = _qs.strip(string.punctuation + string.whitespace)
            material = mapping(
                IDENTIFIERS_MEDIUM_TYPES,
                val_q,
            ) or "PRINT_VERSION"

        return {
            "scheme": "ISBN",
            "value": val,
            "material": material
        }

    identifier_a = get_identifier("a")
    if identifier_a and identifier_a not in _identifiers:
        _identifiers.append(identifier_a)

    identifier_z = get_identifier("z")
    if identifier_z and identifier_z not in _identifiers:
        _identifiers.append(identifier_z)

    return _identifiers


@model.over("languages", "^0410_")
@for_each_value
@out_strip
def languages(self, key, value):
    """Translates languages fields."""
    lang = clean_val("a", value, str).lower()
    try:
        return pycountry.languages.lookup(lang).alpha_3.upper()
    except (KeyError, AttributeError, LookupError):
        raise UnexpectedValue(subfield="a")


@model.over("subjects", "^050_4")
@filter_list_values
def subjects_loc(self, key, value):
    """Translates subject classification."""
    _subjects = self.get("subjects", [])
    subject = {"scheme": "LOC", "value": clean_val("a", value, str)}
    if subject not in _subjects:
        _subjects.append(subject)
    return _subjects


@model.over("subjects", "^08204")
@filter_list_values
def subjects_dewey(self, key, value):
    """Translates subject classification."""
    _subjects = self.get("subjects", [])
    subject = {"scheme": "DEWEY", "value": clean_val("a", value, str)}
    if subject not in _subjects:
        _subjects.append(subject)
    return _subjects


@model.over("edition", "^250__")
@out_strip
def edition(self, key, value):
    """Translate edition field."""
    val_a = (
        clean_val("a", value, str)
        .lower()
        .replace("ed.", "")
        .replace("edition", "")
        .strip(string.punctuation + string.whitespace)
    )

    # use the value if not in the mappings
    return mapping(
        EDITIONS,
        val_a,
        default_val=val_a,
    )


@model.over("imprint", "^260__")
@out_strip
def imprint(self, key, value):
    """Translate imprint field."""
    _publication_year = self.get("publication_year")
    if _publication_year:
        raise UnexpectedValue(subfield="e", message="doubled publication year")
    pub_year = clean_val("c", value, str).strip(
        string.punctuation + string.whitespace
    )
    self["publication_year"] = pub_year

    return {
        "publisher": clean_val("b", value, str).strip(
            string.punctuation.replace(")", "") + string.whitespace
        ),  # keep last parenthesis
        "place": clean_val("a", value, str).strip(
            string.punctuation + string.whitespace
        ),
    }


@model.over("number_of_pages", "^300__")
@out_strip
def number_of_pages(self, key, value):
    """Translate number of pages."""
    numbers = re.findall(r"(\d+) p", clean_val("a", value, str))
    return numbers[0] if numbers else None


@model.over("abstract", "^520__")
@out_strip
def abstract(self, key, value):
    """Translate abstract."""
    return clean_val("a", value, str)


@model.over("_serial", "^4901_")
@filter_list_values
@for_each_value
def serial(self, key, value):
    """Translate serial."""
    volume = clean_val("v", value, str)
    if volume:
        volume = re.findall(r"\d+", volume)

    serial_title = clean_val("a", value, str, req=True).strip(
        string.punctuation + string.whitespace
    )

    words_to_replace = ["ser.", "Ser."]
    for word in words_to_replace:
        # check if the word on the end of the title
        if re.search(f"{word}$", serial_title):
            serial_title = rreplace(serial_title, word, "series", 1)

    return {
        "title": serial_title.strip(
            string.punctuation + string.whitespace
        ),
        "volume": volume[0] if volume else None,
    }


@model.over("table_of_content", "^5051_")
@out_strip
def table_of_content(self, key, value):
    """Translate table of content."""
    return clean_val("a", value, str).split("--")


@model.over("keywords", "^650_0")
@filter_list_values
def keywords(self, key, value):
    """Translate keywords."""
    _keywords = self.get("keywords", [])

    keyword = {
        "source": "SAFARI",
        "value": clean_val("a", value, str, req=True).strip(
            string.punctuation + string.whitespace
        ),
    }

    if keyword not in _keywords:
        _keywords.append(keyword)
    return _keywords
