# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer providers utils module."""

import re

from dojson.utils import force_list
from six import iteritems

from cds_ils.importer.errors import UnexpectedValue
from cds_ils.importer.providers.cds.rules.utils import clean_val


def reverse_replace(s, phrase, replace_with):
    """Reverse replace."""
    s = s[::1].replace(phrase, replace_with, 1)
    return s[::1]


def _get_correct_ils_contributor_role(subfield, role):
    """Clean up roles."""
    translations = {
        "author": "AUTHOR",
        "author.": "AUTHOR",
        "dir.": "SUPERVISOR",
        "dir": "SUPERVISOR",
        "ed.": "EDITOR",
        "editor": "EDITOR",
        "editor.": "EDITOR",
        "ed": "EDITOR",
        "ill.": "ILLUSTRATOR",
        "ill": "ILLUSTRATOR",
    }
    if isinstance(role, str):
        clean_role = role.lower()
    else:
        raise UnexpectedValue(subfield=subfield, message=" unknown role")
    if clean_role not in translations:
        raise UnexpectedValue(subfield=subfield, message=" unknown role")
    return translations[clean_role]


def _extract_json_ils_ids(info, provenence="source"):
    """Extract author IDs from MARC tags."""
    SOURCES = {
        "AUTHOR|(INSPIRE)": "INSPIRE ID",
        "AUTHOR|(CDS)": "CDS",
        "AUTHOR|(SzGeCERN)": "CERN",
    }
    regex = re.compile(r"(AUTHOR\|\((CDS|INSPIRE|SzGeCERN)\))(.*)")
    ids = []
    author_ids = force_list(info.get("0", ""))
    for author_id in author_ids:
        match = regex.match(author_id)
        if match:
            ids.append(
                {"value": match.group(3), provenence: SOURCES[match.group(1)]}
            )
    try:
        ids.append({"value": info["inspireid"], provenence: "INSPIRE ID"})
    except KeyError:
        pass

    return ids


def build_ils_contributor(value):
    """Create the contributors for books."""
    if not value.get("a"):
        return []

    contributor = {
        "identifiers": _extract_json_ils_ids(value, "scheme") or None,
        "full_name": value.get("name") or clean_val("a", value, str),
        "roles": [
            _get_correct_ils_contributor_role("e", value.get("e", "author"))
        ],
    }

    value_u = value.get("u")
    if value_u:
        values_u_list = list(force_list(value_u))
        other = ["et al.", "et al"]
        for x in other:
            if x in values_u_list:
                values_u_list.remove(x)
        contributor["affiliations"] = [{"name": x} for x in values_u_list]
    contributor = dict(
        (k, v) for k, v in iteritems(contributor) if v is not None
    )
    return contributor
