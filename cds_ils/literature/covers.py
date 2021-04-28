# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Literature covers."""

import urllib
from functools import partial

from flask import current_app
from invenio_app_ils.literature.covers_builder import build_placeholder_urls
from invenio_app_ils.proxies import current_app_ils

MIN_CONTENT_LENGTH = 128


def should_record_have_cover(record):
    """Check if this type of record has cover."""
    if "$schema" in record:
        schema = record["$schema"]
        Document = current_app_ils.document_record_cls
        is_document = schema.endswith(Document._schema)
        Series = current_app_ils.series_record_cls
        is_series = schema.endswith(Series._schema)
        if is_document or is_series:
            return True
    return False


def has_already_cover(cover_metadata={}):
    """Check if record has already valid cover in cover_metadata."""
    return cover_metadata.get("ISBN") or cover_metadata.get("ISSN")


def is_valid_cover(cover_metadata):
    """Fetch all sizes of cover from url and evaluate if they are valid."""
    syndetics_urls = build_syndetic_cover_urls(cover_metadata)
    if syndetics_urls is None:
        return False

    try:
        for size in ["small", "medium", "large"]:
            resp = urllib.request.urlopen(syndetics_urls[size])
            has_error = resp.getcode() != 200
            less_than_1_pixel = (
                int(resp.getheader("Content-Length")) <= MIN_CONTENT_LENGTH
            )
            if has_error or less_than_1_pixel:
                return False
    except Exception:
        return False

    return True


def build_syndetic_cover_urls(cover_metadata):
    """Decorate literature with cover urls for all sizes."""
    client = current_app.config["CDS_ILS_SYNDETIC_CLIENT"]
    url = "https://secure.syndetics.com/index.aspx"

    issn = cover_metadata.get("ISSN")
    if issn:
        scheme = "ISSN"
        scheme_value = issn

    isbn = cover_metadata.get("ISBN")
    if isbn:
        scheme = "ISBN"
        scheme_value = isbn

    if issn or isbn:
        _url = "{url}?client={client}&{scheme}={value}/{size}.gif"
        partial_url = partial(
            _url.format,
            url=url,
            client=client,
            scheme=scheme,
            value=scheme_value,
        )
        return {
            "is_placeholder": False,
            "small": partial_url(size="SC"),
            "medium": partial_url(size="MC"),
            "large": partial_url(size="LC"),
        }
    return None


def build_cover_urls(metadata):
    """Try to build the cover urls else build placeholder urls."""
    cover_metadata = metadata.get("cover_metadata", {})
    syndetics_urls = build_syndetic_cover_urls(cover_metadata)
    return syndetics_urls or build_placeholder_urls()
