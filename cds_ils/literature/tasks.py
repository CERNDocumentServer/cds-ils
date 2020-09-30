# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Literature tasks."""

from celery import shared_task
from invenio_app_ils.proxies import current_app_ils
from invenio_db import db

from .covers import has_already_cover, is_valid_cover, should_record_have_cover


def pick_identifier_with_cover(sender, *args, **kwargs):
    """Triggers async task to set cover metadata of the record."""
    record = kwargs.get("record")
    if record and should_record_have_cover(record):
        pick_identifier_with_cover_task.apply_async((record,))


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


def save_record(record, cover_metadata=None):
    """Updates and saves record to the db."""
    schema = record["$schema"]

    Document = current_app_ils.document_record_cls
    is_document = schema.endswith(Document._schema)
    Series = current_app_ils.series_record_cls
    is_series = schema.endswith(Series._schema)

    assert is_document or is_series

    if is_document:
        record = Document.get_record_by_pid(record["pid"])
        indexer = current_app_ils.document_indexer
    elif is_series:
        record = Series.get_record_by_pid(record["pid"])
        indexer = current_app_ils.series_indexer

    if cover_metadata:
        record["cover_metadata"] = cover_metadata
    else:
        record.pop("cover_metadata", "")  # delete if present

    record.commit()
    db.session.commit()
    indexer.index(record)


@shared_task(ignore_result=True)
def pick_identifier_with_cover_task(record):
    """Set a valid cover identifier to cover metadata, else an empty dict."""
    cover_metadata = record.get("cover_metadata", {})
    identifiers = record.get("identifiers", [])
    if not identifiers:
        if has_already_cover(cover_metadata):
            # record had a cover, but identifiers have been deleted.
            # Remove previous covers
            save_record(record)
        return

    issn_list, isbn_list = create_identifiers_lists(identifiers)
    if has_already_cover(cover_metadata):
        # there is a previous cover, do nothing if still valid
        current_cover_in_identifiers = (
            cover_metadata.get("ISBN") in isbn_list
            or cover_metadata.get("ISSN") in issn_list
        )
        if current_cover_in_identifiers and is_valid_cover(cover_metadata):
            return

    # no previous cover or not valid, revalidate all identifiers
    for value in issn_list:
        new_cover_metadata = {"ISSN": value}
        if is_valid_cover(new_cover_metadata):
            save_record(record, new_cover_metadata)
            return

    for value in isbn_list:
        new_cover_metadata = {"ISBN": value}
        if is_valid_cover(new_cover_metadata):
            save_record(record, new_cover_metadata)
            return

    # previous cover, but no valid identifiers, clean it
    if has_already_cover(cover_metadata):
        save_record(record)
