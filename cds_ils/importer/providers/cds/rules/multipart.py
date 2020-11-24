# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS MARCXML Multipart rules."""

import re
from copy import deepcopy

from dojson.errors import IgnoreKey
from dojson.utils import for_each_value, force_list

from cds_ils.importer.errors import MissingRequiredField, UnexpectedValue

from ...utils import build_ils_contributor
from ..models.multipart import model
from .base import alternative_identifiers as alternative_identifiers_base
from .base import urls as urls_base
from .utils import clean_val, extract_parts, extract_volume_info, \
    extract_volume_number, filter_list_values, out_strip
from .values_mapping import MATERIALS, mapping


def _insert_volume(_migration, volume_number, volume_obj):
    """Find or create the corresponding volume, and insert the attribute."""
    volumes = _migration["volumes"]
    volume_obj = deepcopy(volume_obj)
    volume_obj["volume"] = volume_number
    volumes.append(volume_obj)
    return volume_obj


@model.over("identifiers", "^020__", override=True)
@filter_list_values
@for_each_value
def isbns(self, key, value):
    """Translates isbns stored in the record."""
    _migration = self["_migration"]
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
                "isbn": clean_val("a", value, str),
                "physical_description": volume_info["description"].strip(),
                "is_electronic": val_b is not None,
            }
            _insert_volume(_migration, volume_info["volume"], volume_obj)
            raise IgnoreKey("identifiers")
        if set_search:
            self["physical_description"] = set_search.group(1).strip()
            isbn = {"scheme": "ISBN", "value": val_a}
            return isbn if isbn not in _identifiers else None
        if not volume_info:
            # Try to find a volume number
            volume_number = extract_volume_number(val_u)
            if volume_number:
                # volume, but without description
                volume_obj = {
                    "isbn": clean_val("a", value, str),
                    "is_electronic": val_b is not None,
                }
                _insert_volume(_migration, volume_number, volume_obj)
                raise IgnoreKey("identifiers")
            elif extract_volume_number(val_u, search=True):
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


@model.over("dois", "^0247_", override=True)
@filter_list_values
def dois(self, key, value):
    """Translates DOIs."""
    _migration = self["_migration"]
    _identifiers = self.get("identifiers", [])
    for v in force_list(value):
        val_2 = clean_val("2", v, str)
        if val_2 and val_2 != "DOI":
            raise UnexpectedValue(
                subfield="2", message=" field is not equal to DOI"
            )
        val_q = clean_val("q", v, str, transform="lower")
        volume_info = extract_volume_info(val_q)
        doi = {
            "value": clean_val("a", v, str, req=True),
            "source": clean_val("9", v, str),
            "scheme": "DOI",
        }
        if volume_info:
            # this identifier is for a specific volume
            volume_obj = {
                "doi": doi["value"],
                "material": mapping(
                    MATERIALS, volume_info["description"], raise_exception=True
                ),
                "source": doi["source"],
            }
            _insert_volume(_migration, volume_info["volume"], volume_obj)
        else:
            if re.match(r".* \(.*\)", val_q):
                raise UnexpectedValue(
                    subfield="q",
                    message=" found a volume number but could not extract it",
                )
            doi["material"] = mapping(MATERIALS, val_q, raise_exception=True)
            if doi not in _identifiers:
                _identifiers.append(doi)
    if len(_identifiers) > 0:
        self["identifiers"] = _identifiers


@model.over("alternative_identifiers", "(^035__)|(^036__)", override=True)
def alternative_identifiers(self, key, value):
    """Translates external_system_identifiers fields."""
    return alternative_identifiers_base(self, key, value)


@model.over("barcode", "^088__", override=True)
def barcode(self, key, value):
    """Translates the barcodes."""
    _migration = self["_migration"]
    for v in force_list(value):
        val_a = clean_val("a", v, str)
        val_n = clean_val("n", v, str)
        val_x = clean_val("x", v, str)
        val_9 = clean_val("9", v, str)
        if val_a or val_9:
            if val_n or val_x or val_a and val_9:
                raise UnexpectedValue()
            identifier = {"scheme": "report_number", "value": val_a or val_9}
            if val_9:
                identifier["hidden"] = True
            identifiers = self.get("identifiers", [])
            identifiers.append(identifier)
            self["identifiers"] = identifiers
            raise IgnoreKey("barcode")

        if val_n and val_x:
            volume_number = extract_volume_number(
                val_n, raise_exception=True, subfield="n"
            )
            _insert_volume(_migration, volume_number, {"barcode": val_x})
        elif val_x:
            raise MissingRequiredField(
                subfield="n", message=" this record is missing a volume number"
            )
        else:
            raise MissingRequiredField(
                subfield="x",
                message=" this record is missing a barcode number",
            )
    raise IgnoreKey("barcode")


@model.over("authors", "(^100__)|(^700__)", override=True)
def authors(self, key, value):
    """Translates the authors field."""
    _migration = self["_migration"]
    _authors = _migration.get("authors", [])
    item = build_ils_contributor(value)
    if item and item not in _authors:
        _authors.append(item)
    try:
        if "u" in value:
            other = ["et al.", "et al"]
            val_u = list(force_list(value.get("u")))
            if [i for i in other if i in val_u]:
                _migration["other_authors"] = True
    except UnexpectedValue:
        pass
    _migration["authors"] = _authors
    return list(map(lambda author: author["full_name"], _authors))


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

    volume_title = self.get("title", None)

    _migration = self["_migration"]

    for v in force_list(value):
        # check if it is a multipart monograph
        val_n = clean_val("n", v, str)
        val_p = clean_val("p", v, str)
        val_y = clean_val("y", v, str)
        if not val_n and not val_p:
            raise UnexpectedValue(
                subfield="n", message=" this record is probably not a series"
            )
        if val_p and not val_n:
            raise UnexpectedValue(
                subfield="n",
                message=" volume title exists but no volume number",
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
            obj = {"title": val_p or volume_title}
            if val_y:
                if re.match("\\d+", val_y) and 1600 <= int(val_y) <= 2021:
                    obj["publication_year"] = int(val_y)
                else:
                    raise UnexpectedValue(
                        subfield="y", message=" unrecognized publication year"
                    )
            _insert_volume(_migration, volume_number, obj)
    if not volume_title:
        raise MissingRequiredField(
            subfield="a", message=" this record is missing a main title"
        )

    # series created

    return _migration


@model.over("number_of_volumes", "^300__", override=True)
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


@model.over("multivolume_record_format", "^596__")
def multivolume_record_format(self, key, value):
    """Multivolume kind."""
    val_a = clean_val("a", value, str)
    _migration = self["_migration"]
    if val_a == "MULTIVOLUMES-1":
        parsed = True
    elif val_a == "MULTIVOLUMES-X" or val_a == "MULTIVOLUMES-x":
        parsed = False
    elif val_a == "MULTIVOLUMES-MANUAL":
        raise Exception("This record should not be migrated!")
    else:
        raise UnexpectedValue(
            subfield="a", message=" unrecognized migration multipart tag"
        )
    _migration["multivolume_record_format"] = parsed
    raise IgnoreKey("multivolume_record_format")


@model.over("multipart_id", "^597__")
def multipart_id(self, key, value):
    """Volume serial id."""
    val_a = clean_val("a", value, str)
    _migration = self["_migration"]
    _migration["multipart_id"] = val_a
    raise IgnoreKey("multipart_id")


@model.over("urls", "^8564_", override=True)
def urls(self, key, value):
    """Translates urls field."""
    sub_y = clean_val("y", value, str, default="")
    sub_u = clean_val("u", value, str, req=True)

    _migration = self["_migration"]

    volume_info = extract_volume_info(sub_y) if sub_y else None

    if volume_info:
        # url for a specific volume
        # TODO?
        description = volume_info["description"]
        volume_number = volume_info["volume"]
        if description != "ebook":
            raise UnexpectedValue(subfield="y", message=" unsupported value")
        volume_obj = {
            "url": sub_u,
            "description": description,
        }
        _insert_volume(_migration, volume_info["volume"], volume_obj)
        raise IgnoreKey("urls")
    else:
        return urls_base(self, key, value)
