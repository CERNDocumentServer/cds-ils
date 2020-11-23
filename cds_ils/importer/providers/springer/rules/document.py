# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Springer Importer rules."""
import re

from dojson.errors import IgnoreKey
from dojson.utils import filter_values, for_each_value, force_list
from invenio_app_ils.documents.api import Document

from cds_ils.importer.errors import ManualImportRequired, UnexpectedValue
from cds_ils.importer.providers.cds.rules.utils import clean_val, \
    filter_list_values, out_strip
from cds_ils.importer.providers.springer.springer import model
from cds_ils.importer.providers.utils import _get_correct_ils_contributor_role


# REQUIRED_FIELDS
@model.over("alternative_identifiers", "^001")
@filter_list_values
def recid(self, key, value):
    """Record Identifier."""
    self["provider_recid"] = value
    return [{"scheme": "SPRINGER", "value": value}]


@model.over("agency_code", "^003")
def agency_code(self, key, value):
    """Control number identifier."""
    return value


@model.over("title", "^24510")
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


@model.over("authors", "(^1001_)|(^7001_)")
@filter_list_values
def authors(self, key, value):
    """Translates authors."""
    _authors = self.get("authors", [])

    orcid = clean_val("0", value, str)
    identifiers = None

    if orcid:
        identifiers = [{"scheme": "ORCID", "value": orcid}]
    author = {
        "full_name": clean_val("a", value, str, req=True),
        "identifiers": identifiers,
        "roles": [
            _get_correct_ils_contributor_role("e", clean_val("e", value, str))
        ],
    }
    _authors.append(author)
    return _authors


@model.over("document_type", "^980__")
def document_type(self, key, value):
    """Translate document type."""
    document_type = clean_val("a", value, str)
    if document_type in Document.DOCUMENT_TYPES:
        return document_type
    raise ManualImportRequired(
        subfield="a",
        message="Document type {} is not allowed.".format(document_type),
    )


@model.over("imprint", "^264_1")
@out_strip
def imprint(self, key, value):
    """Translate imprint field."""
    _publication_year = self.get("publication_year")
    if _publication_year:
        raise UnexpectedValue(subfield="e", message="doubled publication year")
    self["publication_year"] = clean_val("c", value, str)

    publisher = ", ".join([entry for entry in value.get("b")])
    return {
        "place": clean_val("a", value, str),
        "publisher": publisher,
        "date": clean_val("c", value, str),
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
                "description": "E-book by Springer",
                "value": clean_val("u", v, str),
            }
        )
    _eitem.update({"urls": urls})
    return _eitem


@model.over("_eitem", "^595__")
@out_strip
def eitem_int_note(self, key, value):
    """Translate eitem internal note."""
    _eitem = self.get("_eitem", {})

    int_note = clean_val("a", value, str)
    _eitem.update({"internal_notes": int_note})
    return _eitem


# OPTIONAL FIELDS


@model.over(
    "identifiers",
    "^020__",
)
@filter_list_values
def identifiers(self, key, value):
    """Translate identifiers."""
    _isbns = self.get("identifiers", [])
    for v in force_list(value):
        subfield_u = clean_val("u", v, str)
        sub_a = clean_val("a", v, str)
        if sub_a:
            isbn = {"value": sub_a, "scheme": "ISBN", "material": subfield_u}
            if isbn not in _isbns:
                _isbns.append(isbn)
    return _isbns


@model.over(
    "identifiers",
    "^024__",
)
@filter_list_values
def identifiers(self, key, value):
    """Translate identifiers."""
    _identifiers = self.get("identifiers", [])
    for v in force_list(value):
        subfield_u = clean_val("u", v, str)
        sub_a = clean_val("a", v, str)
        sub_2 = clean_val("2", v, str)
        if sub_2.lowercase() != "doi":
            raise ManualImportRequired("wrong DOI marc")
        doi = {"value": sub_a, "scheme": "DOI", "material": subfield_u}
        if doi not in _identifiers:
            _identifiers.append(doi)
    return _identifiers


@model.over("subjects", "^050_4")
def subjects_loc(self, key, value):
    """Translates subject classification."""
    _subjects = self.get("subjects", [])

    _subjects.append({"scheme": "LoC", "value": clean_val("a", value, str)})
    return _subjects


@model.over("subjects", "(^082_4)|(^08204)")
def subjects_dewey(self, key, value):
    """Translates subject classification."""
    _subjects = self.get("subjects", [])

    _subjects.append({"scheme": "Dewey", "value": clean_val("a", value, str)})
    return _subjects


@model.over("edition", "^250__")
@out_strip
def edition(self, key, value):
    """Translate edition field."""
    # TODO remove year if present and ed.
    return clean_val("a", value, str)


@model.over("number_of_pages", "^300__")
@out_strip
def number_of_pages(self, key, value):
    """Translate number of pages."""
    pages = clean_val("a", value, str)
    if pages:
        numbers = re.findall(r"\d+", pages)
        return numbers[0] if numbers else None


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


@model.over("open_access", "^5060_")
@out_strip
def open_access(self, key, value):
    """Translate open access."""
    _open_access = clean_val("a", value, str)
    _eitem = self.get("_eitem", {})
    if _open_access.lower() == "open access":
        _eitem["open_access"] = True
        self["_eitem"] = _eitem
    raise IgnoreKey("open_access")


@model.over("abstract", "^520__")
@out_strip
def abstract(self, key, value):
    """Translate abstract."""
    return clean_val("a", value, str)


@model.over("keywords", "(^650_0|^65014|^65024)")
@filter_list_values
def keywords(self, key, value):
    """Translate keywords."""
    _keywords = self.get("keywords", [])

    keyword = {"source": "SPR", "value": clean_val("a", value, str, req=True)}

    if keyword not in _keywords:
        _keywords.append(keyword)
    return _keywords


@model.over("identifiers", "^77608")
@filter_list_values
def id_isbns(self, key, value):
    """Translate identifiers isbn."""
    _identifiers = self.get("identifiers", [])

    isbn_value = clean_val("a", value, str)

    if isbn_value:
        isbn = {
            "scheme": "ISBN",
            "value": clean_val("a", value, str),
            "material": clean_val("u", value, str),
        }

        if isbn not in _identifiers:
            _identifiers.append(isbn)

    return _identifiers


@model.over("_eitem", "^950__")
@out_strip
def eitem_internal_note(self, key, value):
    """Translate item internal note."""
    _eitem = self.get("_eitem", {})
    _eitem["internal_note"] = clean_val("a", value, str)
    return _eitem
