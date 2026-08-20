# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS GOBI Importer rules."""

import re

from dojson.utils import for_each_value, force_list

from cds_ils.importer.errors import UnexpectedValue
from cds_ils.importer.providers.cds.helpers.decorators import (
    filter_list_values,
    out_strip,
)
from cds_ils.importer.providers.cds.helpers.parsers import clean_val
from cds_ils.importer.providers.gobi.gobi import model
from cds_ils.importer.providers.utils import _get_correct_ils_contributor_role, rreplace

# REQUIRED FIELDS


@model.over("alternative_identifiers", "^001")
@filter_list_values
def recid(self, key, value):
    """Record Identifier."""
    self["provider_recid"] = value
    return [{"scheme": "GOBI", "value": value}]


@model.over("agency_code", "^003")
def agency_code(self, key, value):
    """Control number identifier."""
    return value


@model.over("authors", "(^100)|(^700)")
@filter_list_values
def authors(self, key, value):
    """Translates authors."""
    _authors = self.get("authors", [])
    author = {
        "full_name": clean_val("a", value, str, req=True).rstrip(",").rstrip("."),
        "roles": [_get_correct_ils_contributor_role("e", clean_val("e", value, str))],
        "type": "PERSON",
    }
    _authors.append(author)
    return _authors


@model.over("title", "^245")
@out_strip
def title(self, key, value):
    """Translates title."""
    if "title" in self:
        raise UnexpectedValue(message="Title appears more than once")
    title = clean_val("a", value, str, req=True).rstrip(":").rstrip("/")
    if "b" in value:
        subtitle = clean_val("b", value, str).rstrip("/")
        title = f"{title} : {subtitle}"
    title = " ".join(title.split())
    return title


@model.over("imprint", "^264_1")
@out_strip
def imprint(self, key, value):
    """Translate imprint field."""
    _publication_year = self.get("publication_year")
    if _publication_year:
        raise UnexpectedValue(subfield="c", message="doubled publication year")

    year = clean_val("c", value, str)
    if year:
        numbers = re.findall(r"\d{4}", year)
        self["publication_year"] = numbers[0] if numbers else year.strip("[]")

    return {
        "place": clean_val("a", value, str).rstrip(":"),
        "publisher": clean_val("b", value, str).rstrip(","),
    }


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
    _eitem.update({"urls": urls, "source": "GOBI"})
    return _eitem


# OPTIONAL FIELDS


@model.over("identifiers", "^020__")
@filter_list_values
def identifiers(self, key, value):
    """Translate identifiers.

    GOBI records sometimes put the qualifier inline in $a
    (e.g. "9781483392646 (electronic bk.)") instead of a
    separate $q, so it needs stripping with a regex rather
    than relying on clean_val("q", ...).
    """
    _isbns = self.get("identifiers", [])
    for v in force_list(value):
        sub_a = clean_val("a", v, str)
        if sub_a:
            isbn_value = re.sub(r"\s*\(.*\)\s*$", "", sub_a).strip()
            isbn = {"value": isbn_value, "scheme": "ISBN", "material": "DIGITAL"}
            if isbn not in _isbns:
                _isbns.append(isbn)
    return _isbns


@model.over("subjects", "^050_4")
def subjects_loc(self, key, value):
    """Translates subject classification."""
    _subjects = self.get("subjects", [])
    subject = {"scheme": "LOC", "value": clean_val("a", value, str)}
    if subject not in _subjects:
        _subjects.append(subject)
    return _subjects


@model.over("subjects", "(^082_4)|(^08204)")
def subjects_dewey(self, key, value):
    """Translates subject classification."""
    _subjects = self.get("subjects", [])
    subject = {"scheme": "DEWEY", "value": clean_val("a", value, str)}
    if subject not in _subjects:
        _subjects.append(subject)
    return _subjects


@model.over("number_of_pages", "^300__")
@out_strip
def number_of_pages(self, key, value):
    """Translate number of pages."""
    pages = clean_val("a", value, str)
    if pages:
        numbers = re.findall(r"\d+", pages)
        return numbers[0] if numbers else None


@model.over("_serial", "(^490)|(^830)")
@filter_list_values
@for_each_value
def serial(self, key, value):
    """Translate serial."""
    volume = clean_val("v", value, str)
    if volume:
        volume = re.findall(r"\d+", volume)

    serial_title = clean_val("a", value, str, req=True).rstrip(",").rstrip(";").strip()
    serial_title = " ".join(serial_title.split())

    return {
        "title": serial_title,
        "volume": volume[0] if volume else None,
    }


@model.over("table_of_content", "^505")
@out_strip
def table_of_content(self, key, value):
    """Translate table of content.

    GOBI records vary: some use repeated $t subfields
    (chapter-by-chapter), others a single $a with items
    separated by " -- ".
    """
    toc = []
    for v in force_list(value):
        parts = clean_val("t", v, str, multiple_values=True) or []
        if not any(parts):
            a_val = clean_val("a", v, str)
            parts = a_val.split("--") if a_val else []
        toc.extend(p.strip(" -") for p in parts if p and p.strip(" -"))
    return toc


@model.over("keywords", "^650_0")
@filter_list_values
def keywords(self, key, value):
    """Translate keywords."""
    _keywords = self.get("keywords", [])
    keyword = {
        "source": "GOBI",
        "value": clean_val("a", value, str, req=True).rstrip("."),
    }
    if keyword not in _keywords:
        _keywords.append(keyword)
    return _keywords


@model.over("identifiers", "^776")
@filter_list_values
def id_isbns(self, key, value):
    """Translate print-version identifiers."""
    _identifiers = self.get("identifiers", [])
    isbn_values = clean_val("z", value, str, multiple_values=True) or []
    for isbn_value in isbn_values:
        isbn = {
            "scheme": "ISBN",
            "value": isbn_value,
            "material": "PRINT_VERSION",
        }
        if isbn not in _identifiers:
            _identifiers.append(isbn)
    return _identifiers


@model.over("alternative_identifiers", "^776")
@filter_list_values
def id_control_numbers(self, key, value):
    """Translate related record control numbers from 776 $w.

    $w values are formatted like "(DLC)  2015048502" or "(OCoLC)123456"
    -- the bracketed agency code is extracted and used as the scheme,
    since the prefix varies between records.
    """
    _alt_ids = self.get("alternative_identifiers", [])
    control_numbers = clean_val("w", value, str, multiple_values=True) or []
    for cn in control_numbers:
        match = re.match(r"\((?P<agency>[^)]+)\)\s*(?P<number>.+)", cn.strip())
        if match:
            alt_id = {
                "scheme": match.group("agency"),
                "value": match.group("number").strip(),
            }
        else:
            alt_id = {"scheme": "776w", "value": cn.strip()}
        if alt_id not in _alt_ids:
            _alt_ids.append(alt_id)
    return _alt_ids
