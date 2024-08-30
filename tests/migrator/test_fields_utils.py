# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS fields utilities."""

import pytest
from dojson.errors import IgnoreKey

from cds_ils.importer.errors import (
    ManualImportRequired,
    MissingRequiredField,
    UnexpectedValue,
)
from cds_ils.importer.providers.cds.helpers.decorators import (
    filter_list_values,
    out_strip,
    replace_in_result,
)
from cds_ils.importer.providers.cds.helpers.parsers import (
    clean_email,
    clean_str,
    clean_val,
    get_week_start,
    related_url,
)


def test_rel_url():
    """Test if build of related record url works."""
    assert related_url(245432) == "https://cds.cern.ch/record/245432"


@pytest.mark.parametrize(
    "to_clean, regex_format, req, output",
    [
        (" BOOK", None, False, "BOOK"),
        (" BOOK ", None, False, "BOOK"),
        ("201845", r"\d{6}$", False, "201845"),
        ("20-50", r"\d+(?:[\-‐‑‒–—―⁻₋−﹘﹣－]\d+)$", False, "20-50"),
    ],
)
def test_clean_str(to_clean, regex_format, req, output):
    """Test if clean str works correctly"""
    assert clean_str(to_clean, regex_format, req) == output

    assert clean_str("TEST", None, False, transform="lower") == "test"


@pytest.mark.xfail(raises=MissingRequiredField)
def test_clean_str_required():
    """Test if it fails when require val is needed"""
    assert clean_str("", None, req=True)


@pytest.mark.xfail(raises=UnexpectedValue)
def test_clean_str_none():
    """Test if it fails when it gets none value."""
    assert clean_str(None, None, req=False)


@pytest.mark.xfail(raises=UnexpectedValue)
def test_clean_str_regex():
    """Test if it fails when require val is needed"""
    assert clean_str("300500", r"\d+(?:[\-‐‑‒–—―⁻₋−﹘﹣－]\d+)$", req=True)


@pytest.mark.parametrize(
    "subfield, value, var_type, req, default, manual, output",
    [
        ("a", {"a": "CERN"}, str, False, None, None, "CERN"),
        ("a", {"a": "12345"}, int, False, None, None, 12345),
        ("a", {"a": ""}, bool, False, None, None, False),
        ("a", {}, str, True, "TEST", None, "TEST"),
        ("a", {}, int, True, 100, None, 100),
    ],
)
def test_clean_val(subfield, value, var_type, req, default, manual, output):
    """Test if clean value works properly"""

    assert (
        clean_val(subfield, value, var_type, req=req, default=default, manual=manual)
        == output
    )


@pytest.mark.parametrize(
    "subfield, value, var_type, req, default, manual, regexp, output",
    [
        (
            "a",
            {"a": "20-40"},
            str,
            False,
            None,
            None,
            r"\d+(?:[\-‐‑‒–—―⁻₋−﹘﹣－]\d+)$",
            "20-40",
        ),
    ],
)
def test_clean_val_regexp(
    subfield, value, var_type, req, default, manual, regexp, output
):
    assert (
        clean_val(
            subfield,
            value,
            var_type,
            req=req,
            default=default,
            manual=manual,
            regex_format=regexp,
        )
        == output
    )


@pytest.mark.xfail(raises=ManualImportRequired)
def test_clean_val_manual():
    """Test if manual exception is raised properly"""
    assert clean_val("a", {"a": "CERN"}, str, manual=True)


@pytest.mark.xfail(raises=MissingRequiredField)
def test_clean_val_required():
    """Tests if fails when required value missing"""
    assert clean_val("a", {}, str, req=True)


@pytest.mark.xfail(raises=NotImplementedError)
def test_clean_val_type():
    """Tests if fails when unexpected value type"""
    assert clean_val("a", {"a": "CERN"}, float) == "CERN"


def test_clean_email():
    """Test if the email is cleaned properly"""
    assert clean_email("johndoe@cern.ch") == "johndoe@cern.ch"
    assert clean_email("johndoe[CERN]") == "johndoe@cern.ch"
    assert clean_email("johndoe [CERN]") == "johndoe@cern.ch"


def test_get_week_start():
    """Test if the week start date is calculated properly"""
    from datetime import date

    assert get_week_start(2018, 20) == date(2018, 5, 14)
    assert get_week_start(2017, 5) == date(2017, 1, 30)
    assert get_week_start(2016, 52) == date(2016, 12, 26)
    assert get_week_start(2015, 53) == date(2015, 12, 28)
    assert get_week_start(2015, 1) == date(2014, 12, 29)


@pytest.mark.parametrize(
    "phrase, replace_with, key, value, output",
    [
        ("Collaboration", "", None, ["ATLAS Collaboration"], ["ATLAS"]),
        ("ed.", "editor", None, ["main ed."], ["main editor"]),
        ("ed.", "editor", "role", [{"role": "ed."}], [{"role": "editor"}]),
        ("ed.", "editor", None, [], []),
    ],
)
def test_replace_in_result(phrase, replace_with, key, value, output):
    """Test if the replace in result decorator works"""

    @replace_in_result(phrase, replace_with, key)
    def func(*args, **kwargs):
        return value

    assert func() == output


def test_filter_list_values():
    """Test if filtering None and values from list of dict works"""

    @filter_list_values
    def func(self, key, value):
        return value

    assert func(
        None, "key", [{"key": "test", "p": "", "o": None, "s": [], "k": {}}]
    ) == [{"key": "test"}]


@pytest.mark.xfail(raises=IgnoreKey)
def test_filter_list_ignore():
    """Test if raises on empty string or None"""

    @filter_list_values
    def func(self, key, value):
        return value

    func(None, "key", [{"key": ""}])


@pytest.mark.xfail(raises=IgnoreKey)
def test_filter_list_ignore_empty():
    """Test if fails with empty list"""

    @filter_list_values
    def func(self, key, value):
        return value

    func(None, "key", [])


@pytest.mark.parametrize(
    "value_in, out",
    [
        (["test1", "test2", ""], ["test1", "test2"]),
        ("test", "test"),
    ],
)
def test_out_strip(value_in, out):
    """Test if out strip works properly"""

    @out_strip
    def func(self, key, value):
        return value

    assert func(None, None, value_in) == out


@pytest.mark.xfail(raises=IgnoreKey)
def test_out_ignore_str():
    """Test if fails on empty strings"""

    @out_strip
    def func(self, key, value):
        return value

    assert func(None, None, "")


@pytest.mark.xfail(raises=IgnoreKey)
def test_out_ignore_list():
    """Test if fails on empty strings"""

    @out_strip
    def func(self, key, value):
        return value

    assert func(None, None, ["", {}])


def test_out_ignore_type():
    """Test if fails on empty strings"""

    @out_strip
    def func(self, key, value):
        return value

    assert func(None, None, {"p": "zzz"}) == {"p": "zzz"}
