# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Springer Importer rules."""
import re

from dojson.errors import IgnoreKey
from dojson.utils import for_each_value, force_list
from invenio_app_ils.documents.api import Document

from cds_ils.importer.errors import ManualImportRequired, UnexpectedValue
from cds_ils.importer.providers.cds.helpers.decorators import (
    filter_list_values,
    out_strip,
)
from cds_ils.importer.providers.cds.helpers.parsers import clean_val
from cds_ils.importer.providers.springer.springer import model
from cds_ils.importer.providers.utils import _get_correct_ils_contributor_role, rreplace


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


@model.over("title", "^245")
@out_strip
def title(self, key, value):
    """Translates title."""
    if "title" in self:
        raise UnexpectedValue(message="Ambiguous title")

    if "b" in value:
        _alternative_titles = self.get("alternative_titles", [])
        subtitle = clean_val("b", value, str).rstrip("/")
        _alternative_titles.append({"value": subtitle, "type": "SUBTITLE"})
        self["alternative_titles"] = _alternative_titles

    title = clean_val("a", value, str, req=True).rstrip("/")
    # remove excess white spaces
    title = " ".join(title.split())

    return title


@model.over("authors", "(^100)|(^700)")
@filter_list_values
def authors(self, key, value):
    """Translates authors."""
    _authors = self.get("authors", [])
    orcid = clean_val("0", value, str)
    identifiers = None

    if orcid:
        identifiers = [{"scheme": "ORCID", "value": orcid}]
    author = {
        "full_name": clean_val("a", value, str, req=True).rstrip("."),
        "identifiers": identifiers,
        "roles": [_get_correct_ils_contributor_role("e", clean_val("e", value, str))],
        "type": "PERSON",
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
    self["publication_year"] = clean_val("c", value, str).rstrip(".")

    return {
        "place": clean_val("a", value, str).rstrip(":"),
        "publisher": "Springer",
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
        material = clean_val("u", v, str)
        sub_a = clean_val("a", v, str)
        if sub_a:
            isbn = {"value": sub_a, "scheme": "ISBN", "material": "DIGITAL"}
            if isbn not in _isbns:
                _isbns.append(isbn)
    return _isbns


@model.over(
    "identifiers",
    "(^024__)|(^024_7)|(^0247_)",
)
@filter_list_values
def identifiers(self, key, value):
    """Translate identifiers."""
    _identifiers = self.get("identifiers", [])
    for v in force_list(value):
        subfield_u = clean_val("u", v, str) or "DIGITAL"
        sub_a = clean_val("a", v, str)
        sub_2 = clean_val("2", v, str)
        if sub_2.lower() != "doi":
            raise ManualImportRequired("wrong DOI marc")
        doi = {"value": sub_a, "scheme": "DOI", "material": subfield_u}
        if doi not in _identifiers:
            _identifiers.append(doi)
    return _identifiers


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


@model.over("edition", "^250__")
@out_strip
def edition(self, key, value):
    """Translate edition field."""
    _edition = (
        clean_val("a", value, str).replace("ed.", "").replace("edition", "").rstrip(".")
    )
    _edition = re.sub(r"\d{4}", "", _edition)
    return _edition.strip()


@model.over("number_of_pages", "^300__")
@out_strip
def number_of_pages(self, key, value):
    """Translate number of pages."""
    pages = clean_val("a", value, str)
    if pages:
        numbers = re.findall(r"\d+", pages)
        return numbers[0] if numbers else None


@model.over("_serial", "^490")
@filter_list_values
@for_each_value
def serial(self, key, value):
    """Translate serial."""
    subfield_x = clean_val("x", value, str)
    identifiers = None

    if subfield_x:
        issn_value = rreplace(subfield_x, ";", "").strip()
        if issn_value:
            identifiers = [{"scheme": "ISSN", "value": issn_value}]

    volume = clean_val("v", value, str)
    if volume:
        volume = re.findall(r"\d+", volume)

    serial_title = clean_val("a", value, str, req=True).rstrip(",").rstrip(";").strip()

    words_to_replace = ["ser.", "Ser."]
    for word in words_to_replace:
        # check if the word on the end of the title
        if re.search(f"{word}$", serial_title):
            serial_title = rreplace(serial_title, word, "series")

    # remove excess white spaces
    serial_title = " ".join(serial_title.split())

    return {
        "title": serial_title.strip(),
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

    keyword = {
        "source": "SPR",
        "value": clean_val("a", value, str, req=True).rstrip("."),
    }

    if keyword not in _keywords:
        _keywords.append(keyword)
    return _keywords


@model.over("identifiers", "^776")
@filter_list_values
def id_isbns(self, key, value):
    """Translate identifiers isbn."""
    _identifiers = self.get("identifiers", [])

    isbn_value = clean_val("a", value, str) or (clean_val("z", value, str))
    material = clean_val("u", value, str)

    if isbn_value:
        isbn = {
            "scheme": "ISBN",
            "value": clean_val("z", value, str),
            "material": "PRINT_VERSION",
        }

        if isbn not in _identifiers:
            _identifiers.append(isbn)

    return _identifiers


@model.over("_eitem", "^950__")
@out_strip
def eitem_internal_note(self, key, value):
    """Translate item internal note."""
    _eitem = self.get("_eitem", {})
    _eitem["internal_notes"] = clean_val("a", value, str)
    return _eitem
