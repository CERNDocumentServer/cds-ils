# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Literature tasks."""

import urllib

from celery import shared_task
from invenio_app_ils.documents.api import Document
from invenio_app_ils.documents.indexer import DocumentIndexer
from invenio_app_ils.series.api import Series
from invenio_app_ils.series.indexer import SeriesIndexer
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search

from .covers import build_syndetic_cover_urls, has_already_cover, \
    should_record_have_cover

MIN_CONTENT_LENGTH = 128


def pick_identifier_with_cover(sender, *args, **kwargs):
    """Triggers async task to set cover metadata of the record."""
    record = kwargs.get("record", {})
    if should_record_have_cover(record):
        pick_identifier_with_cover_task.apply_async((record,))


def is_valid_cover(cover_metadata):
    """Fetch all sizes of cover from url and evaluate if they are valid."""
    partial_record = {"cover_metadata": cover_metadata}
    urls = build_syndetic_cover_urls(partial_record)
    if urls is None:
        return False

    try:
        for size in ["small", "medium", "large"]:
            resp = urllib.request.urlopen(urls[size])
            has_error = resp.getcode() != 200
            less_than_1_pixel = (
                int(resp.getheader("Content-Length")) <= MIN_CONTENT_LENGTH
            )
            if has_error or less_than_1_pixel:
                return False
    except Exception:
        return False

    return True


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
    schema = record.get("$schema")
    if schema.endswith("series-v1.0.0.json"):
        record = Series.get_record_by_pid(record["pid"])
        indexer = SeriesIndexer()
    else:
        record = Document.get_record_by_pid(record["pid"])
        indexer = DocumentIndexer()

    record["cover_metadata"] = cover_metadata
    record.commit()
    db.session.commit()
    indexer.index(record)


@shared_task(ignore_result=True)
def pick_identifier_with_cover_task(record):
    """Set an valid cover identifier to cover metadata, else an empty dict."""
    if not should_record_have_cover(record):
        return

    if has_already_cover(record) and is_valid_cover(record["cover_metadata"]):
        return

    identifiers = record.get("identifiers", [])
    if not identifiers:
        return

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

    # Check if identifier exists in metadata but is invalid (and no other valid
    # identifier was found).
    # The function will never go inside this if condition if an update signal
    # was fired because of `save_record` since the latter will commit in the
    # cover_metadata either an empty dict {} or a valid identifier (so the
    # function will have already returned in the above ifs).
    # The only reason the function will reach inside this is either if a
    # creation of a record just happened and `preemtively..` function added an
    # invalid identifier to the cover_metadata, or if an update happened to the
    # record by a user (not by `save_record`) and the previous identifier was
    # invalid/non-existent and the updated one is invalid or it was deleted.
    if record["cover_metadata"] != {}:
        save_record(record, {})
