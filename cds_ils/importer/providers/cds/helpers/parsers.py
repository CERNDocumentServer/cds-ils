# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS MARCXML rules utils."""

import re
from datetime import date, timedelta

from dojson.utils import force_list

from cds_ils.importer.errors import (
    ManualImportRequired,
    MissingRequiredField,
    UnexpectedValue,
)

MAX_PAGES_NUMBER = 8192

RE_STR_VOLUME_PREFIX = (
    r"(?:(?:[Vv](?:ol(?:ume)?)?|[Pp]"
    r"(?:art(?:ie)?|t)?|[Tt](?:eil)?|[Bb]d|"
    r"[Tt]ome?|course|conference|fasc(?:icule)?"
    r"|book|unit|suppl|Tafeln|Tomo)[\s\.]*)"
)

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

    # If we have more than one occurrence of pages its UnexpectedValue
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
        "physical_description": physical_description,
    }


def is_volume_index(value):
    """Determine if the string is a volume number."""
    regex = RE_VOLUME_NUMBER
    result = regex.search(value.strip())
    if result:
        return True
    else:
        return False


def extract_volume_number(value):
    """Extract the volume number from a string, returns None if not matched."""
    return value.replace("v.", "").replace("v .", "").strip()


def extract_volume_info(value):
    """Extract volume number and physical description."""
    result = re.search(r"(.*?)\(+(?P<volume>[^\(]+)\)+", value.strip())
    if result:
        return dict(
            description=result.group(1).strip(),
            volume=extract_volume_number(result.groupdict()["volume"]),
        )
    return None


def related_url(value):
    """Builds related records urls."""
    return "{0}{1}".format("https://cds.cern.ch/record/", value)


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
    if callable(transform):
        cleaned = transform(cleaned)
    elif transform and hasattr(cleaned, transform):
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
    multiple_values=False,
):
    """
    Tests values using common rules.

    :param subfield: marcxml subfield indicator
    :param value: marcxml value
    :param var_type: expected type for value to be cleaned
    :param req: specifies if the value is required in the end schema
    :param regex_format: specifies if the value should have a pattern
    :param default: if value is missing and required it outputs default
    :param manual: if the value should be cleaned manually during the migration
    :param transform: string transform function (or callable)
    :param multiple_values: allow multiple values in subfield
    :return: cleaned output value
    """

    def _clean(value_to_clean):
        if value_to_clean is not None:
            try:
                if var_type is str:
                    return clean_str(value_to_clean, regex_format, req, transform)
                elif var_type is bool:
                    return bool(value_to_clean)
                elif var_type is int:
                    return int(value_to_clean)
                else:
                    raise NotImplementedError
            except ValueError:
                raise UnexpectedValue(subfield=subfield)
            except TypeError:
                raise UnexpectedValue(subfield=subfield)
            except (UnexpectedValue, MissingRequiredField) as e:
                e.subfield = subfield
                e.message += str(force_list(value))
                raise e

    to_clean = value.get(subfield)

    if manual and to_clean:
        raise ManualImportRequired(subfield=subfield)
    if req and to_clean is None:
        if default:
            return default
        raise MissingRequiredField(subfield=subfield)

    is_tuple = type(to_clean) is tuple
    if is_tuple and not multiple_values:
        raise UnexpectedValue(subfield=subfield)

    if multiple_values:
        if is_tuple:
            cleaned_values = []
            for v in to_clean:
                cleaned_values.append(_clean(v))
            return cleaned_values
        else:
            # always return a list when `multiple_values` is True
            return [_clean(to_clean)]
    else:
        return _clean(to_clean)


def clean_email(value):
    """Cleans the email field."""
    if value:
        email = (
            value.strip().replace(" [CERN]", "@cern.ch").replace("[CERN]", "@cern.ch")
        )
        return email


def get_week_start(year, week):
    """Translates cds book year week format to starting date."""
    d = date(year, 1, 1)
    if d.weekday() > 3:
        d = d + timedelta(7 - d.weekday())
    else:
        d = d - timedelta(d.weekday())
    dlt = timedelta(days=(week - 1) * 7)
    return d + dlt
