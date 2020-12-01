# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS acquisition order migrator API.

Acquisition Order CDS fields:
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
           request_type: acq-book
      borrower_comments: NULL
      only_this_edition: None
          library_notes: {}
            budget_code:
  overdue_letter_number: 0
    overdue_letter_date: 0000-00-00 00:00:00


CDS statuses          ILS AcqOrder statuses
cancelled          -> "CANCELLED"
new                -> "PENDING"
on order           -> "ORDERED"
proposal-on order  -> "ORDERED"
received           -> "RECEIVED"
proposal-received  -> "RECEIVED" It was doc request and resolved as acq order
"""

import json

import click
from invenio_db import db

from cds_ils.migrator.acquisition.vendors import get_vendor_pid_by_legacy_id
from cds_ils.migrator.api import bulk_index_records, import_record, \
    model_provider_by_rectype
from cds_ils.migrator.errors import AcqOrderError, ItemMigrationError
from cds_ils.migrator.items.api import get_item_by_barcode
from cds_ils.migrator.utils import get_acq_ill_notes, get_cost, get_date, \
    get_migration_document_pid, get_patron_pid

DEFAULT_ITEM_MEDIUM = "ELECTRONIC"
LIBRARIAN_IDS = [
    5,
    7,
    39,
    446,
    690,
    1068,
    1399,
    3221,
    3688,
    4019,
    4388,
    4461,
    4824,
    6150,
    6420,
    7241,
    7983,
    8762,
    9579,
]


def get_status(record):
    """Map CDS status to a valid ILS status."""
    mapping = {
        "cancelled": "CANCELLED",
        "new": "PENDING",
        "on order": "ORDERED",
        "proposal-on order": "ORDERED",
        "received": "RECEIVED",
    }
    try:
        return mapping[record["status"]]
    except KeyError:
        raise AcqOrderError(
            "Unknown status for acquisition order!\n{}".format(record)
        )


def get_recipient(record):
    """Calculate recipient value."""
    budget_code = record.get("budget_code")
    if not budget_code:
        if record.get("id_crcBORROWER") in LIBRARIAN_IDS:
            return "LIBRARY"
        raise AcqOrderError(
            "Could not find `budget_code` for record!\n{}".format(record)
        )

    budget_code = budget_code.lower()
    bookshop_values = ["bs", "bookshop", "19500"]
    if budget_code in bookshop_values:
        return "BOOKSHOP"

    library_values = ["library", "73306", "73307"]
    if budget_code in library_values:
        return "LIBRARY"

    if (
        budget_code == "cash"
        or budget_code.isnumeric()  # when value is 11111
        or budget_code[1:].isnumeric()  # when value is T1111
    ):
        return "PATRON"

    raise AcqOrderError(
        "Could not match `budget_code` to recipient value!\n{}".format(record)
    )


def create_order_line(record):
    """Create an OrderLine."""
    try:
        item = get_item_by_barcode(record["barcode"])
        document_pid = item.get("document_pid")
        item_medium = item.get("medium")
    except ItemMigrationError:
        document_pid = get_migration_document_pid()
        item_medium = DEFAULT_ITEM_MEDIUM

    new_order_line = dict(
        document_pid=document_pid,
        patron_pid=get_patron_pid(record),
        recipient=get_recipient(record),
        medium=item_medium,
        payment_mode="MIGRATED_UNKNOWN",
        copies_ordered=1,  # default 1 because is required
    )

    total_price = get_cost(record)
    if total_price:
        new_order_line.update(total_price=total_price)

    if record.get("budget_code"):
        new_order_line.update(budget_code=record.get("budget_code"))

    return new_order_line


def migrate_order(record):
    """Create a order record for ILS."""
    new_order = dict(
        legacy_id=record["legacy_id"],
        order_lines=[create_order_line(record)],
        status=get_status(record),
    )

    order_date = record["request_date"]
    if order_date:
        new_order.update(order_date=get_date(order_date))

    vendor_pid = get_vendor_pid_by_legacy_id(record["id_crcLIBRARY"])
    new_order.update(vendor_pid=vendor_pid)

    # Optional fields
    grand_total = get_cost(record)
    if grand_total:
        new_order.update(grand_total=grand_total)

    expected_delivery_date = record.get("expected_date")
    if expected_delivery_date:
        new_order.update(
            expected_delivery_date=get_date(expected_delivery_date)
        )

    received_date = record.get("arrival_date")
    if received_date:
        new_order.update(received_date=get_date(received_date))

    notes = get_acq_ill_notes(record)
    if notes:
        new_order.update(notes=notes)

    return new_order


def import_orders_from_json(dump_file, include=None):
    """Imports orders from JSON data files."""
    dump_file = dump_file[0]

    click.echo("Importing acquisition orders ..")
    with click.progressbar(json.load(dump_file)) as input_data:
        ils_records = []
        for record in input_data:
            model, provider = model_provider_by_rectype("acq-order")
            ils_record = import_record(
                migrate_order(record),
                model,
                provider,
                legacy_id_key="legacy_id",
            )

            ils_records.append(ils_record)
        db.session.commit()
    bulk_index_records(ils_records)
