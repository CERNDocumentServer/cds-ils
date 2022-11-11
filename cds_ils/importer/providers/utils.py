# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer providers utils module."""

import re
import string

from dojson.utils import force_list
from six import iteritems

from cds_ils.importer.errors import UnexpectedValue
from cds_ils.importer.providers.cds.helpers.parsers import clean_val


def _get_correct_ils_contributor_role(subfield, role, raise_unexpected=False):
    """Clean up roles."""
    translations = {
        "author": "AUTHOR",
        "author.": "AUTHOR",
        "dir.": "SUPERVISOR",
        "dir": "SUPERVISOR",
        "supervisor": "SUPERVISOR",
        "ed.": "EDITOR",
        "editor": "EDITOR",
        "editor.": "EDITOR",
        "ed": "EDITOR",
        "ill.": "ILLUSTRATOR",
        "ill": "ILLUSTRATOR",
        "ed. et al.": "EDITOR",
    }
    clean_role = None
    if role is None:
        return "AUTHOR"
    if isinstance(role, str):
        clean_role = role.lower()
    elif isinstance(role, list) and role and role[0]:
        clean_role = role[0].lower()
    elif raise_unexpected:
        raise UnexpectedValue(subfield=subfield, message="unknown author role")

    if clean_role not in translations or clean_role is None:
        return "AUTHOR"

    return translations[clean_role]


def _extract_json_ils_ids(info, provenance="scheme"):
    """Extract author IDs from MARC tags."""
    SOURCES = {
        "AUTHOR|(INSPIRE)": "INSPIRE ID",
    }
    regex = re.compile(r"(AUTHOR\|\((INSPIRE)\))(.*)")
    ids = []
    author_ids = force_list(info.get("0", ""))
    for author_id in author_ids:
        match = regex.match(author_id)
        if match:
            ids.append({"value": match.group(3), provenance: SOURCES[match.group(1)]})
    try:
        ids.append({"value": info["inspireid"], provenance: "INSPIRE ID"})
    except KeyError:
        pass

    author_orcid = info.get("k")
    if author_orcid:
        ids.append({"value": author_orcid, provenance: "ORCID"})

    return ids


def build_ils_contributor(value):
    """Create the contributors for books."""
    if not value.get("a"):
        return []

    role = _get_correct_ils_contributor_role("e", value.get("e", "author"))
    contributor = {
        "identifiers": _extract_json_ils_ids(value, "scheme") or None,
        "full_name": value.get("name") or clean_val("a", value, str),
        "alternative_names": [],
        "type": "PERSON",
    }
    if role:
        contributor.update({"roles": [role]})

    subfield_q = clean_val("q", value, str)
    if subfield_q:
        contributor.update({"alternative_names": [subfield_q]})

    value_u = value.get("u")
    if value_u:
        values_u_list = list(force_list(value_u))
        other = ["et al.", "et al"]
        for x in other:
            if x in values_u_list:
                values_u_list.remove(x)
        contributor["affiliations"] = [{"name": x} for x in values_u_list]
    contributor = dict((k, v) for k, v in iteritems(contributor) if v is not None)
    return contributor


def rreplace(s, old, new, occurrence=1):
    """Reverse replace."""
    li = s.rsplit(old, occurrence)
    return new.join(li)
