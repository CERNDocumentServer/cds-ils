# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2017, 2018 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""Books fields."""

from __future__ import absolute_import, print_function, unicode_literals

from cds_dojson.marc21.fields.books.errors import ManualMigrationRequired, \
    MissingRequiredField, UnexpectedValue
from cds_dojson.marc21.fields.books.utils import extract_parts, \
    extract_volume_number, is_excluded
from cds_dojson.marc21.fields.utils import clean_val, filter_list_values, \
    out_strip
from dojson.errors import IgnoreKey
from dojson.utils import filter_values, for_each_value

from cds_ils.importer.providers.cds.cds import model

from .base import alternative_titles as alternative_titles_base


@model.over("alternative_titles", "(^246__)|(^242__)")
@filter_list_values
def alternative_titles(self, key, value):
    """Alternative titles."""
    _alternative_titles = self.get("alternative_titles", [])

    if key == "242__":
        _alternative_titles += alternative_titles_base(self, key, value)
    elif key == "246__":
        if ("n" in value and "p" not in value) or (
            "n" not in value and "p" in value
        ):
            raise MissingRequiredField(subfield="n or p")

        if "p" in value:
            _migration = self.get("_migration", {})
            if "volumes" not in _migration:
                _migration["volumes"] = []

            val_n = clean_val("n", value, str)
            _migration["volumes"].append(
                {
                    "volume": extract_volume_number(
                        val_n, raise_exception=True
                    ),
                    "title": clean_val("p", value, str),
                }
            )
            _migration["is_multipart"] = True
            _migration["record_type"] = "multipart"
            self["_migration"] = _migration
            raise IgnoreKey("alternative_titles")
        else:
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


@model.over("number_of_pages", "^300__")  # item
def number_of_pages(self, key, value):
    """Translates number_of_pages fields."""
    val = clean_val("a", value, str)
    if is_excluded(val):
        raise IgnoreKey("number_of_pages")

    parts = extract_parts(val)
    if parts["has_extra"]:
        raise UnexpectedValue(subfield="a")
    if parts["physical_copy_description"]:
        self["physical_copy_description"] = parts["physical_copy_description"]
    if parts["number_of_pages"]:
        return str(parts["number_of_pages"])
    raise UnexpectedValue(subfield="a")


@model.over("title", "^245__")
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
