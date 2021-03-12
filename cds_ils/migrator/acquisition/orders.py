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
                  'year': ''} or {'recid':}
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
import logging

import click
from flask import current_app
from invenio_app_ils.proxies import current_app_ils
from invenio_db import db
from invenio_pidstore.errors import PIDDoesNotExistError

from cds_ils.literature.api import get_record_by_legacy_recid
from cds_ils.migrator.acquisition.vendors import get_vendor_pid_by_legacy_id
from cds_ils.migrator.api import import_record
from cds_ils.migrator.default_records import MIGRATION_VENDOR_PID
from cds_ils.migrator.errors import AcqOrderError, ItemMigrationError, \
    VendorError
from cds_ils.migrator.handlers import acquisition_order_exception_handler, \
    json_records_exception_handlers
from cds_ils.migrator.items.api import get_item_by_barcode
from cds_ils.migrator.utils import find_correct_document_pid, \
    get_acq_ill_notes, get_cost, get_date, get_migration_document_pid, \
    get_patron_pid

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
        "requested": "PENDING",
        "on order": "ORDERED",
        "proposal-on order": "ORDERED",
        "received": "RECEIVED",
        "proposal-received": "RECEIVED",
    }
    try:
        return mapping[record["status"]]
    except KeyError:
        raise AcqOrderError(
            "Unknown status {} for acquisition order {}".format(
                record["status"], record["legacy_id"]
            )
        )


def get_recipient(record):
    """Calculate recipient value."""
    budget_code = record.get("budget_code")
    legacy_patron_id = record.get("id_crcBORROWER")

    if not budget_code:
        if legacy_patron_id in LIBRARIAN_IDS:
            return "LIBRARY"
        return "PATRON"

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
    return "PATRON"


def create_order_line(record, order_status):
    """Create an OrderLine."""
    document_cls = current_app_ils.document_record_cls
    item_medium = None
    barcode = record.get("barcode").replace("No barcode associated", "")
    item_medium = DEFAULT_ITEM_MEDIUM

    try:
        if barcode:
            item = get_item_by_barcode(barcode)
            document_pid = item["document_pid"]
            item_medium = item.get("medium", DEFAULT_ITEM_MEDIUM)
        else:
            document_pid = find_correct_document_pid(record)
    except ItemMigrationError:
        document_pid = find_correct_document_pid(record)

    if document_pid != get_migration_document_pid():
        document = document_cls.get_record_by_pid(document_pid)
        if document["document_type"] == "BOOK":
            item_medium = "PAPER"

    new_order_line = dict(
        document_pid=document_pid,
        patron_pid=get_patron_pid(record),
        recipient=get_recipient(record),
        medium=item_medium,
        payment_mode="MIGRATED_UNKNOWN",
        copies_ordered=1,  # default 1 because is required
    )

    if order_status == "RECEIVED":
        new_order_line.update({"copies_received": 1})

    total_price = get_cost(record)
    if total_price:
        new_order_line.update(total_price=total_price)

    if record.get("budget_code"):
        new_order_line.update(
            payment_mode="BUDGET_CODE", budget_code=record.get("budget_code")
        )

    return new_order_line


def validate_order(record):
    """Validate order."""
    has_anonymous_patron = False

    for order_line in record["order_lines"]:
        if order_line["patron_pid"] in ["-1", "-2"]:
            has_anonymous_patron = True

    if has_anonymous_patron and record["status"] in ["PENDING", "ORDERED"]:
        raise AcqOrderError(
            f"Order {record['legacy_id']} "
            f"has anonymous patron while being in active state."
        )


def migrate_order(record):
    """Create a order record for ILS."""
    status = get_status(record)

    new_order = dict(
        legacy_id=record["legacy_id"],
        order_lines=[create_order_line(record, status)],
        status=status,
    )

    order_date = record["request_date"]
    if order_date:
        new_order.update(order_date=get_date(order_date))
    else:
        new_order.update(order_date="1970-01-01")

    # Optional fields
    if status == "CANCELLED":
        new_order.update(cancel_reason="MIGRATED/UNKNOWN")

    grand_total = get_cost(record)
    if grand_total:
        new_order.update(grand_total=grand_total)

    try:
        vendor_pid = get_vendor_pid_by_legacy_id(
            record["id_crcLIBRARY"], grand_total
        )
    except VendorError as e:
        vendor_pid = MIGRATION_VENDOR_PID
    new_order.update(vendor_pid=vendor_pid)

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

    validate_order(new_order)

    return new_order


def import_orders_from_json(
    dump_file, rectype="acq-order", raise_exceptions=False
):
    """Imports orders from JSON data files."""
    click.echo("Importing acquisition orders ..")
    with click.progressbar(json.load(dump_file)) as input_data:
        for record in input_data:
            click.echo('Processing order "{}"...'.format(record["legacy_id"]))
            try:
                ils_record = import_record(
                    migrate_order(record),
                    rectype=rectype,
                    legacy_id_key="legacy_id",
                    mint_legacy_pid=False
                )
            except Exception as exc:
                handler = acquisition_order_exception_handler.get(
                    exc.__class__
                )
                if handler:
                    handler(
                        exc,
                        legacy_id=record["legacy_id"],
                        barcode=record["barcode"],
                        rectype=rectype,
                    )
                    if raise_exceptions:
                        raise exc
                else:
                    db.session.rollback()
                    logger = logging.getLogger(f"{rectype}s_logger")
                    logger.error(
                        str(exc),
                        extra=dict(
                            legacy_id=record["legacy_id"],
                            new_pid=None,
                            status="ERROR",
                        ),
                    )
                    raise exc
