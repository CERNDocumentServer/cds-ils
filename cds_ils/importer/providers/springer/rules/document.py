# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Springer Importer rules."""

from cds_dojson.marc21.fields.books.errors import UnexpectedValue
from cds_dojson.marc21.fields.utils import clean_val, filter_list_values, \
    out_strip
from dojson.utils import for_each_value, force_list
from invenio_app_ils.documents.api import Document

from cds_ils.importer.errors import ManualImportRequired
from cds_ils.importer.providers.springer.springer import model
from cds_ils.importer.providers.utils import _get_correct_ils_contributor_role


# REQUIRED_FIELDS
@model.over("provider_recid", "^001")
def recid(self, key, value):
    """Record Identifier."""
    return value


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


@model.over("subjects", "^0504_")
@for_each_value
def subjects(self, key, value):
    """Translates subject classification."""
    _subjects = self.get("subjects")

    _subjects.append({"scheme": "TODO", "value": clean_val("a", value, str)})
    return _subjects


@model.over("subjects", "^0824_")
@for_each_value
def subjects(self, key, value):
    """Translates subject classification."""
    _subjects = self.get("subjects")

    _subjects.append({"scheme": "TODO", "value": clean_val("a", value, str)})
    return _subjects
