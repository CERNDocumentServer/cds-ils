# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Literature tasks."""

import urllib

from celery import shared_task
from invenio_db import db

from .covers import build_syndetic_cover_urls, has_already_cover, \
    is_record_with_cover

MIN_CONTENT_LENGTH = 128


def pick_identifier_with_cover(sender, *args, **kwargs):
    """Triggers async task to set cover metadata of the record."""
    record = kwargs.get("record", {})
    if is_record_with_cover(record):
        pick_identifier_with_cover_task.apply_async((record,))


def is_valid_cover(cover_metadata):
    """Fetch a cover from url and evaluate if it is valid."""
    partial_record = {"cover_metadata": cover_metadata}
    url = build_syndetic_cover_urls(partial_record)['small']
    try:
        resp = urllib.request.urlopen(url)
        is_success = resp.getcode() == 200
        more_than_1_pixel = resp.get("Content-Length", 0) > MIN_CONTENT_LENGTH
    except Exception:
        return None

    if is_success and more_than_1_pixel:
        return resp
    return None


def create_identifiers_lists(identifiers):
    """Splits identifiers in two lists."""
    issn_list = []
    isbn_list = []

    for ident in identifiers:
        if ident["scheme"] == "ISSN":
            issn_list.append(ident["value"])

        if ident["scheme"] == "ISBN":
            isbn_list.append(ident["value"])

    return issn_list, isbn_list


def save_record(record, cover_metadata):
    """Updates and saves record to the db."""
    record["cover_metadata"] = cover_metadata
    record.commit()
    db.session.commit()


@shared_task(ignore_result=True)
def pick_identifier_with_cover_task(record):
    """Set record cover metadata ISBN with valid cover."""
    if not is_record_with_cover(record):
        return

    if has_already_cover(record) and is_valid_cover(record):
        return

    identifiers = record.get("identifiers", [])
    if not identifiers:
        return

    record.setdefault("cover_metadata", {})
    issn_list, isbn_list = create_identifiers_lists(identifiers)

    for value in issn_list:
        cover_metadata = {"ISSN": value}
        if is_valid_cover(cover_metadata):
            save_record(record, cover_metadata)
            return

    for value in isbn_list:
        cover_metadata = {"ISBN": value}
        if is_valid_cover(cover_metadata):
            save_record(record, cover_metadata)
            return
