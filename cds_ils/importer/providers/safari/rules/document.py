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
from cds_ils.importer.providers.cds.helpers.decorators import (
    filter_empty_dict_values,
    filter_list_values,
    out_strip,
)
from cds_ils.importer.providers.cds.helpers.parsers import clean_val
from cds_ils.importer.providers.cds.rules.values_mapping import (
    EDITIONS,
    IDENTIFIERS_MEDIUM_TYPES,
    mapping,
)
from cds_ils.importer.providers.safari.safari import model
from cds_ils.importer.providers.utils import _get_correct_ils_contributor_role, rreplace


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


@model.over("authors", "(^100)|(^7001)")
@filter_list_values
def authors(self, key, value):
    """Translates authors."""
    _authors = self.get("authors", [])
    clean_roles = None

    roles = clean_val("e", value, str, multiple_values=True)
    role = _get_correct_ils_contributor_role("e", roles)
    if role:
        clean_roles = [role.strip(string.punctuation + string.whitespace)]

    author = {
        "full_name": clean_val("a", value, str, req=True).strip(
            string.punctuation + string.whitespace
        ),
        "roles": clean_roles,
        "type": "PERSON",
    }
    _authors.append(author)
    return _authors


@model.over("title", "(^2451)|(^2450)")
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


@model.over("alternative_titles", "^246")
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
    _eitem_type = _eitem.get("_type", "e-book")

    urls = []
    for v in force_list(value):
        urls.append(
            {
                "description": _eitem_type,
                "value": clean_val("u", v, str),
            }
        )
    _eitem.update({"urls": urls})
    return _eitem


# OPTIONAL FIELDS


@model.over("identifiers", "^020*_")
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
        if _qs and _qs[0]:
            val_q = _qs[0].strip(string.punctuation + string.whitespace)
            mapped = mapping(IDENTIFIERS_MEDIUM_TYPES, val_q)
            material = mapped or "PRINT_VERSION"

        return {"scheme": "ISBN", "value": val, "material": material}

    identifier_a = get_identifier("a")
    if identifier_a and identifier_a not in _identifiers:
        _identifiers.append(identifier_a)

    identifier_z = get_identifier("z")
    if identifier_z and identifier_z not in _identifiers:
        _identifiers.append(identifier_z)

    return _identifiers


@model.over("languages", "^041")
@for_each_value
@out_strip
def languages(self, key, value):
    """Translates languages fields."""
    lang = clean_val("a", value, str).lower()
    try:
        return pycountry.languages.lookup(lang).alpha_3.upper()
    except (KeyError, AttributeError, LookupError):
        raise UnexpectedValue(subfield="a")


@model.over("subjects", "(^050_4)|(^05004)|(^05000)|(^05010)|(^05014)")
@filter_list_values
def subjects_loc(self, key, value):
    """Translates subject classification."""
    _subjects = self.get("subjects", [])
    subject = {"scheme": "LOC", "value": clean_val("a", value, str)}
    if subject not in _subjects:
        _subjects.append(subject)
    return _subjects


@model.over("subjects", "(^08204)|(^082_4)|(^08200)")
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


@model.over("imprint", "(^260__)|(^264_1)|(^264_2)|(^264_4)")
@filter_empty_dict_values
def imprint(self, key, value):
    """Translate imprint field.

    The year, publisher and place can be in multiple fields.
    Keep only the value from the first found.
    """
    pub_year = self.get("publication_year")
    if not pub_year and "c" in value:
        pub_year = clean_val("c", value, str)
        if pub_year:
            only_digits = re.findall(r"\d+", pub_year)
            if only_digits:
                self["publication_year"] = only_digits[0]

    publisher = self.get("imprint", {}).get("publisher")
    # use previously set value first, otherwise check if present here
    if not publisher and "b" in value:
        publishers = clean_val("b", value, str, multiple_values=True)
        if publishers:
            # keep last parenthesis
            publisher = publishers[0].strip(
                string.punctuation.replace(")", "") + string.whitespace
            )

    place = self.get("imprint", {}).get("place")
    # use previously set value first, otherwise check if present here
    if not place and "a" in value:
        places = clean_val("a", value, str, multiple_values=True)
        if places:
            place = places[0].strip(string.punctuation + string.whitespace)

    return {"publisher": publisher, "place": place}


@model.over("number_of_pages", "^300__")
@out_strip
def number_of_pages(self, key, value):
    """Translate number of pages."""
    numbers = re.findall(r"(\d+) p", clean_val("a", value, str))
    return numbers[0] if numbers else None


@model.over("abstract", "^520")
@out_strip
def abstract(self, key, value):
    """Translate abstract."""
    if "b" in value:
        return f"{clean_val('a', value, str)} {clean_val('b', value, str)}"
    return clean_val("a", value, str)


@model.over("_serial", "(^4901_)|(^4900_)")
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
            serial_title = rreplace(serial_title, word, "series")

    return {
        "title": serial_title.strip(string.punctuation + string.whitespace),
        "volume": volume[0] if volume else None,
    }


@model.over("table_of_content", "(^5051)|(^5058)")
@out_strip
def table_of_content(self, key, value):
    """Translate table of content."""
    return clean_val("a", value, str).split("--")


@model.over("table_of_content", "^5050")
@out_strip
def table_of_content_additional(self, key, value):
    """Alternative TOC transformation."""
    _toc = self.get("table_of_content", [])
    for v in force_list(value):
        if "t" in v:
            val_t = clean_val("t", v, str, multiple_values=True)
            _toc += val_t
    if "a" in value:
        return table_of_content(self, key, value)
    return _toc


@model.over("keywords", "(^650)")
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
