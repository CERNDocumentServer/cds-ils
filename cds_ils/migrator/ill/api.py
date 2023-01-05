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
import logging

import click
from invenio_app_ils.patrons.api import SystemAgent
from invenio_app_ils.proxies import current_app_ils
from invenio_circulation.proxies import current_circulation
from invenio_db import db

from cds_ils.importer.vocabularies_validator import validator as vocabulary_validator
from cds_ils.migrator.api import import_record
from cds_ils.migrator.constants import CDS_ILS_FALLBACK_CREATION_DATE
from cds_ils.migrator.default_records import MIGRATION_PROVIDER_PID
from cds_ils.migrator.errors import (
    BorrowingRequestError,
    ItemMigrationError,
    ProviderError,
)
from cds_ils.migrator.handlers import json_records_exception_handlers
from cds_ils.migrator.items.api import get_item_by_barcode
from cds_ils.migrator.loans.api import validate_loan
from cds_ils.migrator.providers.api import get_provider_by_legacy_id
from cds_ils.migrator.utils import (
    find_correct_document_pid,
    get_acq_ill_notes,
    get_cost,
    get_date,
    get_patron_pid,
)

records_logger = logging.getLogger("borrowing_requests_logger")

VOCABULARIES_FIELDS = {
    "payment": {
        "mode": {
            "source": "json",
            "type": "ill_payment_mode",
        },
        "debit_cost": {
            "currency": {
                "source": "json",
                "type": "currencies",
            },
        },
    },
    "total": {
        "currency": {
            "source": "json",
            "type": "currencies",
        },
    },
    "type": {
        "source": "json",
        "type": "ill_item_type",
    },
}


def get_status(record):
    """Map CDS status to a valid ILS status."""
    mapping = {
        "cancelled": "CANCELLED",
        "on loan": "ON_LOAN",
        "requested": "REQUESTED",
        "new": "PENDING",
        "returned": "RETURNED",
    }
    try:
        return mapping[record["status"]]
    except KeyError:
        raise BorrowingRequestError(
            "Unknown status for Borrowing Request!\n{}".format(record)
        )


def get_type(record):
    """Get ILL type from legacy request_type."""
    ill_type = "MIGRATED_UNKNOWN"

    if record["request_type"] == "article":
        ill_type = "DIGITAL"

    if record["request_type"] == "book":
        ill_type = "PHYSICAL_COPY"

    return ill_type


def validate_ill(record):
    """Validate borrowing request."""
    has_anonymous_patron = record["patron_pid"] in ["-1", "-2"]

    if has_anonymous_patron and record["status"] in ["ON_LOAN", "REQUESTED"]:
        raise BorrowingRequestError(
            f"Order {record['legacy_id']} "
            f"has anonymous patron while being in active state."
        )


def clean_record_json(record):
    """Create a record for ILS."""
    barcode = (
        record.get("barcode")
        .replace("No barcode associated", "")
        .replace("No barcode asociated", "")
    )
    status = get_status(record)
    try:
        if barcode:
            item = get_item_by_barcode(barcode)
            document_pid = item.get("document_pid")
        else:
            document_pid = find_correct_document_pid(record)
    except ItemMigrationError:
        document_pid = find_correct_document_pid(record)

    try:
        # library_pid
        provider = get_provider_by_legacy_id(
            record["id_crcLIBRARY"], provider_type="LIBRARY"
        )
        provider_pid = provider.pid.pid_value
    except ProviderError as e:
        provider_pid = MIGRATION_PROVIDER_PID

    new_record = dict(
        document_pid=document_pid,
        legacy_id=record.get("legacy_id"),
        provider_pid=provider_pid,
        patron_pid=get_patron_pid(record),
        status=status,
        type=get_type(record),
    )

    # Optional fields
    if status == "CANCELLED":
        new_record.update(cancel_reason="MIGRATED/UNKNOWN")

    expected_delivery_date = record.get("expected_date")
    if expected_delivery_date:
        new_record.update(expected_delivery_date=get_date(expected_delivery_date))

    received_date = record.get("arrival_date")
    if received_date:
        new_record.update(received_date=get_date(received_date))

    request_date = record.get("request_date")
    if request_date:
        new_record.update(request_date=get_date(request_date))

    # former return date is the new due date of the borrowing request
    due_date = record.get("return_date")
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

    validate_ill(new_record)

    vocabulary_validator.validate(VOCABULARIES_FIELDS, new_record)

    return new_record


def create_loan_when_ongoing(ill, legacy_record):
    """Create a loan for the ongoing borrowing request."""
    default_location_pid_value, _ = current_app_ils.get_default_location_pid

    if ill["status"] != "ON_LOAN":
        return

    patron_pid = ill["patron_pid"]
    item_pid = {"value": ill.pid.pid_value, "type": ill.pid.pid_type}
    document_pid = ill["document_pid"]

    loan_dict = dict(
        patron_pid=str(patron_pid),
        transaction_location_pid=default_location_pid_value,
        transaction_user_pid=str(SystemAgent.id),
        document_pid=document_pid,
        item_pid=item_pid,
        state="ITEM_ON_LOAN",
        start_date=ill["received_date"],
        # former due date of borrowing request becomes due date of the loan
        end_date=legacy_record.get("due_date", CDS_ILS_FALLBACK_CREATION_DATE),
    )

    validate_loan(loan_dict, item_pid["value"], borrower_id=patron_pid)

    loan = import_record(
        loan_dict, rectype="loan", legacy_id="ILL loan", mint_legacy_pid=False
    )
    current_circulation.loan_indexer().index(loan)
    db.session.commit()


def import_ill_borrowing_requests_from_json(
    dump_file, raise_exceptions=False, rectype="borrowing-request"
):
    """Imports borrowing requests from JSON data files."""
    click.echo("Importing borrowing requests ..")
    with click.progressbar(json.load(dump_file)) as input_data:
        for record in input_data:
            try:
                ill = import_record(
                    clean_record_json(record),
                    rectype=rectype,
                    legacy_id=record["legacy_id"],
                )
                # create a loan for ongoing ILL
                create_loan_when_ongoing(ill, record)

            except Exception as exc:
                handler = json_records_exception_handlers.get(exc.__class__)
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
                    raise exc
        db.session.commit()
