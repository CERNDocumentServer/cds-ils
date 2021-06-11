# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Series Importer api."""

from elasticsearch_dsl import Q
from invenio_app_ils.proxies import current_app_ils


def search_series_by_isbn(isbn):
    """Find series by ISBN."""
    series_search = current_app_ils.series_search_cls()
    search = series_search.query(
        "bool",
        must=[
            Q("term", identifiers__scheme="ISBN"),
            Q("term", identifiers__value=isbn),
        ],
    )
    return search


def search_series_by_issn(issn):
    """Find series by ISSN."""
    series_search = current_app_ils.series_search_cls()
    search = series_search.query(
        "bool",
        must=[
            Q("term", identifiers__scheme="ISSN"),
            Q("term", identifiers__value=issn),
        ],
    )
    return search


def search_series_by_title(title):
    """Find series by title."""
    series_search = current_app_ils.series_search_cls()
    search = series_search.query("query_string", query=f"title:\"{title}\"")
    return search
