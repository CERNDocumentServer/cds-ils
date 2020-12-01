# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS ILL borrowing request migrator API.

Borrowing Request CDS fields:

              legacy_id: 1
         id_crcBORROWER: 2
                barcode: J00227767
period_of_interest_from: 2010-08-18 00:00:00
  period_of_interest_to: 2011-08-18 00:00:00
          id_crcLIBRARY: 0
           request_date: 0000-00-00 00:00:00
          expected_date: 0000-00-00 00:00:00
           arrival_date: 2010-08-18 00:00:00
               due_date: 2010-09-17 00:00:00
            return_date: 0000-00-00 00:00:00
                 status: returned
                   cost: 0 EUR
              item_info: {
                  'publisher': '',
                  'isbn': '',
                  'title': '',
                  'authors': '',
                  'edition': '',
                  'place': '',
                  'year': ''}
           request_type: book
      borrower_comments: NULL
      only_this_edition: None
          library_notes: {}
            budget_code:
  overdue_letter_number: 0
    overdue_letter_date: 0000-00-00 00:00:00


CDS statuses  -  ILS BorrowingRequest statuses

new           ?  ids: 55952,55463,55245,55128: resolve all new before migration
cancelled     -> CANCELLED - migrated
returned      -> RETURNED - migrated
on loan       -> ON_LOAN - migrated - 35 results, create loan?
received      -> REQUESTED - until library advices otherwise
requested     -> REQUESTED - migrated - 8 results
"""

import json

import click
from elasticsearch_dsl import Q
from invenio_app_ils.ill.api import Library
from invenio_app_ils.ill.proxies import current_ils_ill
from invenio_db import db

from cds_ils.migrator.api import bulk_index_records, import_record, \
    model_provider_by_rectype
from cds_ils.migrator.errors import BorrowingRequestError, ItemMigrationError
from cds_ils.migrator.items.api import get_item_by_barcode
from cds_ils.migrator.utils import get_acq_ill_notes, get_cost, get_date, \
    get_migration_document_pid, get_patron_pid


def get_status(record):
    """Map CDS status to a valid ILS status."""
    mapping = {
        "cancelled": "CANCELLED",
        "on loan": "ON_LOAN",
        "received": "REQUESTED",
        "requested": "REQUESTED",
        "returned": "RETURNED",
    }
    try:
        return mapping[record["status"]]
    except KeyError:
        raise BorrowingRequestError(
            "Unknown status for Borrowing Request!\n{}".format(record)
        )


def get_library_by_legacy_id(legacy_id):
    """Search for library by legacy id."""
    search = current_ils_ill.library_search_cls().query(
        "bool", filter=[Q("term", legacy_id=legacy_id)]
    )
    result = search.execute()
    hits_total = result.hits.total.value
    if not result.hits or hits_total < 1:
        raise BorrowingRequestError(
            "no library found with legacy id {}".format(legacy_id)
        )
    elif hits_total > 1:
        raise BorrowingRequestError(
            "found more than one library with legacy id {}".format(legacy_id)
        )
    else:
        return current_ils_ill.library_record_cls.get_record_by_pid(
            result.hits[0].pid
        )


def get_type(record):
    """Get ILL type from legacy request_type."""
    ill_type = "MIGRATED_UNKNOWN"

    if record["request_type"] == "article":
        ill_type = "ELECTRONIC"

    if record["request_type"] == "book":
        ill_type = "PHYSICAL_COPY"

    return ill_type


def migrate_to_ils(record):
    """Create a record for ILS."""
    document_pid = None
    try:
        item = get_item_by_barcode(record["barcode"])
        document_pid = item.get("document_pid")
    except ItemMigrationError:
        document_pid = get_migration_document_pid()

    # library_pid
    library = get_library_by_legacy_id(record["id_crcLIBRARY"])
    library_pid = library.pid.pid_value

    new_record = dict(
        document_pid=document_pid,
        legacy_id=record.get("legacy_id"),
        library_pid=library_pid,
        patron_pid=get_patron_pid(record),
        status=get_status(record),
        type=get_type(record),
    )

    # Optional fields
    expected_delivery_date = record.get("expected_date")
    if expected_delivery_date:
        new_record.update(
            expected_delivery_date=get_date(expected_delivery_date)
        )

    received_date = record.get("arrival_date")
    if received_date:
        new_record.update(received_date=get_date(received_date))

    request_date = record.get("request_date")
    if request_date:
        new_record.update(request_date=get_date(request_date))

    due_date = record.get("due_date")
    if due_date:
        new_record.update(due_date=get_date(due_date))

    total = get_cost(record)
    if total:
        new_record.update(total=total)

    notes = get_acq_ill_notes(record)
    if notes:
        new_record.update(notes=notes)

    budget_code = record.get("budget_code")
    if budget_code:
        new_record.update(budget_code=budget_code)

    return new_record


def import_ill_borrowing_requests_from_json(dump_file):
    """Imports borrowing requests from JSON data files."""
    dump_file = dump_file[0]
    model, provider = model_provider_by_rectype("borrowing-request")

    click.echo("Importing borrowing requests ..")
    with click.progressbar(json.load(dump_file)) as input_data:
        ils_records = []
        for record in input_data:
            ils_record = import_record(
                migrate_to_ils(record),
                model,
                provider,
                legacy_id_key="legacy_id",
            )
            ils_records.append(ils_record)
        db.session.commit()
    bulk_index_records(ils_records)
