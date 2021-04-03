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

from ..cds import get_helper_dict
from ..helpers.decorators import filter_list_values, out_strip
from ..helpers.eitems import clean_url_provider
from ..helpers.parsers import clean_val, extract_parts, extract_volume_info, \
    extract_volume_number
from ..models.multipart import model
from .base import alternative_identifiers as alternative_identifiers_base
from .base import alternative_titles
from .base import urls as urls_base
from .values_mapping import IDENTIFIERS_MEDIUM_TYPES, mapping


def _insert_volume(_migration, volume_number, volume_obj, field_key="volumes"):
    """Find or create the corresponding volume, and insert the attribute."""
    assert field_key in [
        "volumes",
        "items",
        "volumes_identifiers",
        "volumes_urls",
    ]
    volumes = _migration.get(field_key, [])
    volume_obj = deepcopy(volume_obj)
    volume_obj["volume"] = volume_number
    volumes.append(volume_obj)
    _migration[field_key] = volumes
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
        # if set found it means that the isbn is for the whole multipart
        set_search = re.search(r"(.*?)\(set\.*\)", val_u)
        if set_search:
            self["physical_description"] = set_search.group(1).strip()
            isbn = {"scheme": "ISBN", "value": val_a}
            return isbn if isbn not in _identifiers else None

        # try to extract volume description
        volume_info = extract_volume_info(val_u)
        physical_description = None
        if volume_info:
            physical_description = volume_info["description"].strip()

        # extract volume number
        volume_number = extract_volume_number(val_u, search=True)
        if volume_number:
            volume_obj = {
                "identifiers": [{"value": clean_val("a", value, str),
                                 "scheme": "ISBN"}],
            }
            if physical_description:
                volume_obj.update(
                    {"physical_description": physical_description}
                )
            _insert_volume(
                _migration,
                volume_number,
                volume_obj,
                field_key="volumes_identifiers",
            )
        else:
            # if no volume number, then the physical
            # description and id belongs to the multipart
            self["physical_description"] = val_u
            isbn = {"scheme": "ISBN", "value": val_a}
            return isbn if isbn not in _identifiers else None
    elif not val_u and val_a:
        # if no volume info but only isbn,
        # it belongs to the multipart
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
    volume_info = None
    material = None
    for v in force_list(value):
        val_2 = clean_val("2", v, str)
        if val_2 and val_2 != "DOI":
            raise UnexpectedValue(
                subfield="2", message=" field is not equal to DOI"
            )
        val_q = clean_val("q", v, str, transform="lower")

        if val_q:
            volume_info = extract_volume_info(val_q)
            if volume_info:
                material = mapping(
                    IDENTIFIERS_MEDIUM_TYPES,
                    volume_info["description"].upper(),
                    raise_exception=True,
                )
        doi = {
            "value": clean_val("a", v, str, req=True),
            "scheme": "DOI",
        }

        if volume_info:
            # this identifier is for a specific volume
            if material:
                doi.update(
                    {  # WARNING! vocabulary document_identifiers_materials
                        "material": material
                    })
            volume_obj = {"identifiers": [doi]}
            _insert_volume(
                _migration,
                volume_info["volume"],
                volume_obj,
                field_key="volumes_identifiers",
            )
        else:
            # if a value in parentheses but does not match the volume regex
            if val_q:
                if re.match(r".* \(.*\)", val_q):
                    raise UnexpectedValue(
                        subfield="q",
                        message=" found a volume "
                                "number but could not extract it",
                    )
                # WARNING! vocabulary document_identifiers_materials
                doi["material"] = mapping(
                    IDENTIFIERS_MEDIUM_TYPES, val_q.upper(),
                    raise_exception=True
                )
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
            identifier = {"scheme": "REPORT_NUMBER", "value": val_a or val_9}
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
            _insert_volume(
                _migration,
                volume_number,
                {"barcode": val_x},
                field_key="items",
            )
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


@model.over("title", "^245__", override=True)
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


@model.over("alternative_titles", "^246__", override=True)
def volumes_titles(self, key, value):
    """Translates volumes titles."""
    volume_title = self.get("title", None)

    _migration = self["_migration"]
    _migration["is_multipart"] = True
    _alternative_titles = self.get("alternative_titles", [])

    for v in force_list(value):
        # check if it is a multipart monograph
        val_n = clean_val("n", v, str)
        val_p = clean_val("p", v, str)
        val_y = clean_val("y", v, str)

        val_a = clean_val("a", v, str)
        val_b = clean_val("b", v, str)

        if not val_n and not val_p:
            raise UnexpectedValue(
                subfield="n", message=" this record is probably not a series"
            )
        if val_p and not val_n:
            raise UnexpectedValue(
                subfield="n",
                message=" volume title exists but no volume number",
            )

        volume_number = extract_volume_number(
            val_n, raise_exception=True, subfield="n"
        )
        obj = {"title": val_p or volume_title}
        if val_y:
            if re.match("\\d+", val_y) and len(val_y) == 4:
                obj["publication_year"] = val_y
            else:
                raise UnexpectedValue(
                    subfield="y", message=" unrecognized publication year"
                )
        _insert_volume(_migration, volume_number, obj)
        if val_a:
            _alternative_titles.append(
                {
                    "value": val_a,
                    "type": "ALTERNATIVE_TITLE",
                }
            )
        if val_b:
            _alternative_titles.append(
                {
                    "value": val_b,
                    "type": "SUBTITLE",
                }
            )
        if _alternative_titles:
            return _alternative_titles
        raise IgnoreKey("alternative_titles")
    if not volume_title:
        raise MissingRequiredField(
            subfield="a", message=" this record is missing a main title"
        )

    raise IgnoreKey("alternative_titles")


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
    val_x = clean_val("x", value, str)
    parsed_a = extract_parts(val_a)
    if parsed_a["number_of_pages"]:
        self["number_of_pages"] = str(parsed_a["number_of_pages"])
    if not parsed_a["number_of_pages"] and ("v" in val_a or "vol" in val_a):
        _volumes = re.findall(r"\d+", val_a)
        if _volumes:
            return _volumes[0]
    if val_x:
        if val_x == "volume":
            raise IgnoreKey("number_of_volumes")
        elif val_x.lower() in ["phys.desc.", "phys.desc"]:
            self["physical_description"] = val_a
            raise IgnoreKey("number_of_volumes")
    raise IgnoreKey("number_of_volumes")


@model.over("multivolume_record", "^596__")
def multivolume_record(self, key, value):
    """Mark record with many volumes inside."""
    val_a = clean_val("a", value, str)
    _migration = self["_migration"]
    if val_a == "MULTIVOLUMES1":
        parsed = False
    elif val_a == "MULTIVOLUMESX" or val_a == "MULTIVOLUMESx":
        parsed = True
    elif val_a == "MULTIVOLUMES-MANUAL":
        raise Exception("This record should not be migrated!")
    else:
        raise UnexpectedValue(
            subfield="a", message=" unrecognized migration multipart tag"
        )
    _migration["multivolume_record"] = parsed
    raise IgnoreKey("multivolume_record")


@model.over("multipart_id", "^597__")
def multipart_id(self, key, value):
    """Volume serial id."""
    val_a = clean_val("a", value, str)
    _migration = self["_migration"]
    _migration["multipart_id"] = val_a.upper()
    raise IgnoreKey("multipart_id")


@model.over("urls", "^8564_", override=True)
def urls(self, key, value):
    """Translates urls field."""
    sub_y = clean_val("y", value, str, default="")
    sub_u = clean_val("u", value, str, req=True)

    _migration = self["_migration"]

    volume_info = extract_volume_info(sub_y) if sub_y else None

    if volume_info:
        description = volume_info["description"]
        volume_number = volume_info["volume"]
        if description not in ["ebook", "e-book", "e-proceedings"]:
            raise UnexpectedValue(subfield="y", message=" unsupported value")

        # create partial child object for each volume with its own _migration
        volume_migration_dict = {"_migration": deepcopy(get_helper_dict(
            record_type='document'))}

        url_obj = clean_url_provider(url_value=sub_u, url_description=sub_y,
                                     record_dict=volume_migration_dict)
        volume_obj = {**volume_migration_dict}

        if url_obj:
            volume_obj.update({"urls": [url_obj]})

        _insert_volume(
            _migration, volume_number, volume_obj, field_key="volumes_urls"
        )
        raise IgnoreKey("urls")
    else:
        return urls_base(self, key, value)


@model.over("alternative_titles", "^242__")
@filter_list_values
def alternative_titles_multipart(self, key, value):
    """Translate alternative titles."""
    return alternative_titles(self, key, value)
