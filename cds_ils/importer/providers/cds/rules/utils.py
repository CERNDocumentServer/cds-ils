# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS MARCXML rules utils."""
import functools
import re
from datetime import date, timedelta

from dojson.errors import IgnoreKey

from cds_ils.importer.errors import ManualImportRequired, \
    MissingRequiredField, UnexpectedValue

MAX_PAGES_NUMBER = 8192

RE_STR_VOLUME_PREFIX = r"(?:(?:[Vv](?:ol(?:ume)?)?|[Pp]" \
                       r"(?:art(?:ie)?|t)?|[Tt](?:eil)?|[Bb]d|" \
                       r"[Tt]ome?|course|conference|fasc(?:icule)?" \
                       r"|book|unit|suppl|Tafeln|Tomo)[\s\.]*)"

RE_STR_ROMAN_NUMERAL = r"(?:(?:IX|IV|V?I{1,3})|X{1,3}(?:IX|IV|V?I{0,3}))"
RE_STR_VOLUME_SUFFIX = r"(\d{{1,4}}|\d\d?[a-zA-Z]|[a-zA-Z]\d|[A-H]|{})".format(
    RE_STR_ROMAN_NUMERAL
)
RE_STR_VOLUME = r"(?:{}?{})".format(RE_STR_VOLUME_PREFIX, RE_STR_VOLUME_SUFFIX)
RE_STR_SPECIAL = r"[^0-9A-Za-zÀ-ÿ\-/]"

RE_VOLUME_NUMBER = re.compile(
    r"(?:^|{}){}(?:$|{})".format(RE_STR_SPECIAL, RE_STR_VOLUME, RE_STR_SPECIAL)
)
RE_VOLUME_INFO = re.compile(r"(.*?)\({}\)".format(RE_STR_VOLUME))


def is_excluded(value):
    """Validate if field 300 should be excluded."""
    exclude = [
        "mul. p",
        "mult p",
        "mult. p",
        "mult. p.",
        "mult. p",
        "multi p",
        "multi pages",
    ]
    if not value or value.strip().lower() in exclude:
        return True
    return False


def extract_number_of_pages(value):
    """Extract number of pages from 300 if exists."""
    res = re.findall(r"([0-9]+) *p", value, flags=re.IGNORECASE)

    # If we have more than one occurency of pages its UnexpectedValue
    if len(res) == 1 and int(res[0]) < MAX_PAGES_NUMBER:
        return int(res[0])
    return None


def extract_physical_description(value):
    """Extract physical description from 300 if any."""
    res = re.findall(
        r"([0-9]+ \w[CD\-ROM|DVD\-ROM|diskette|VHS]+)",
        value,
        flags=re.IGNORECASE,
    )
    if res:
        return ", ".join(res).upper()
    return None


def extract_parts(value):
    """Split our input to several parts."""
    separators = ["+", ";", ",", ":"]
    res = []
    for sep in separators:
        if sep in value:
            res += value.split(sep)

    valid_parts_count = len(list(filter(is_excluded, res)))

    number_of_pages = extract_number_of_pages(value)
    if number_of_pages:
        valid_parts_count -= 1

    physical_description = extract_physical_description(value)
    if physical_description:
        valid_parts_count -= len(physical_description.split(","))

    return {
        "has_extra": bool(valid_parts_count > 0),
        "number_of_pages": number_of_pages,
        "physical_copy_description": physical_description,
    }


def extract_volume_number(
    value, search=False, raise_exception=False, subfield=None
):
    """Extract the volume number from a string, returns None if not matched."""
    regex = RE_VOLUME_NUMBER
    if search:
        func = regex.search
    else:
        func = regex.match

    result = func(value.strip())
    if result:
        return result.group(1)

    if raise_exception:
        raise MissingRequiredField(
            subfield=subfield, message=" failed to parse volume number"
        )

    return None


def extract_volume_info(value):
    """Extract ISBN, volume number and physical description from 020__u."""
    result = RE_VOLUME_INFO.search(value.strip())
    if result:
        return dict(
            description=result.group(1).strip(),
            volume=result.group(2),
        )
    return None


def related_url(value):
    """Builds related records urls."""
    return "{0}{1}".format("https://cds.cern.ch/record/", value)


def clean_pages_range(pages_subfield, value):
    """Builds pages dictionary."""
    page_regex = r"\d+(?:[\-‐‑‒–—―⁻₋−﹘﹣－]*\d*)$"
    pages_val = clean_val(pages_subfield, value, str, regex_format=page_regex)
    if pages_val:
        pages = re.split(r"[\-‐‑‒–—―⁻₋−﹘﹣－]+", pages_val)
        if len(pages) == 1:
            result = {"page_start": int(pages[0])}
            return result
        else:
            result = {"page_start": int(pages[0]), "page_end": int(pages[1])}
            return result


def clean_str(to_clean, regex_format, req, transform=None):
    """Cleans string marcxml values."""
    if regex_format:
        pattern = re.compile(regex_format)
        match = pattern.match(to_clean)
        if not match:
            raise UnexpectedValue
    try:
        cleaned = to_clean.strip()
    except AttributeError:
        raise UnexpectedValue
    if not cleaned and req:
        raise MissingRequiredField
    if transform and hasattr(cleaned, transform):
        cleaned = getattr(cleaned, transform)()
    return cleaned


def clean_val(
    subfield,
    value,
    var_type,
    req=False,
    regex_format=None,
    default=None,
    manual=False,
    transform=None,
):
    """
    Tests values using common rules.

    :param subfield: marcxml subfield indicator
    :param value: mxrcxml value
    :param var_type: expected type for value to be cleaned
    :param req: specifies if the value is required in the end schema
    :param regex_format: specifies if the value should have a pattern
    :param default: if value is missing and required it outputs default
    :param manual: if the value should be cleaned manually durign the migration
    :param transform: string transform function
    :return: cleaned output value
    """
    to_clean = value.get(subfield)
    if manual and to_clean:
        raise ManualImportRequired
    if req and to_clean is None:
        if default:
            return default
        raise MissingRequiredField
    if to_clean is not None:
        try:
            if var_type is str:
                return clean_str(to_clean, regex_format, req, transform)
            elif var_type is bool:
                return bool(to_clean)
            elif var_type is int:
                return int(to_clean)
            else:
                raise NotImplementedError
        except ValueError:
            raise UnexpectedValue(subfield=subfield)
        except TypeError:
            raise UnexpectedValue(subfield=subfield)


def clean_email(value):
    """Cleans the email field."""
    if value:
        email = (
            value.strip()
            .replace(" [CERN]", "@cern.ch")
            .replace("[CERN]", "@cern.ch")
        )
        return email


def get_week_start(year, week):
    """Translates cds book yearweek format to starting date."""
    d = date(year, 1, 1)
    if d.weekday() > 3:
        d = d + timedelta(7 - d.weekday())
    else:
        d = d - timedelta(d.weekday())
    dlt = timedelta(days=(week - 1) * 7)
    return d + dlt


def replace_in_result(phrase, replace_with, key=None):
    """Replaces string values in list with given string."""

    def the_decorator(fn_decorated):
        def proxy(*args, **kwargs):
            res = fn_decorated(*args, **kwargs)
            if res:
                if not key:
                    return [
                        k.replace(phrase, replace_with).strip() for k in res
                    ]
                else:
                    return [
                        dict(
                            (
                                k,
                                v.replace(phrase, replace_with).strip()
                                if k == key
                                else v,
                            )
                            for k, v in elem.items()
                        )
                        for elem in res
                    ]
            return res

        return proxy

    return the_decorator


def filter_list_values(f):
    """Remove None and blank string values from list of dictionaries."""

    @functools.wraps(f)
    def wrapper(self, key, value, **kwargs):
        out = f(self, key, value)
        if out:
            clean_list = [
                dict((k, v) for k, v in elem.items() if v)
                for elem in out
                if elem
            ]
            clean_list = [elem for elem in clean_list if elem]
            if not clean_list:
                raise IgnoreKey(key)
            return clean_list
        else:
            raise IgnoreKey(key)

    return wrapper


def out_strip(fn_decorated):
    """Decorator cleaning output values of trailing and following spaces."""

    def proxy(self, key, value, **kwargs):
        res = fn_decorated(self, key, value, **kwargs)
        if not res:
            raise IgnoreKey(key)
        if isinstance(res, str):
            # the value is not checked for empty strings here because clean_val
            # does the job, it will be None caught before
            return res.strip()
        elif isinstance(res, list):
            cleaned = [elem.strip() for elem in res if elem]
            if not cleaned:
                raise IgnoreKey(key)
            return cleaned
        else:
            return res

    return proxy
