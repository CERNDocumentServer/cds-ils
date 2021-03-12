# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator API."""

import json
import logging

import click
from flask import current_app
from invenio_app_ils.patrons.api import SystemAgent
from invenio_app_ils.proxies import current_app_ils
from invenio_db import db

from cds_ils.migrator.api import import_record
from cds_ils.migrator.errors import LoanMigrationError
from cds_ils.migrator.handlers import json_records_exception_handlers
from cds_ils.migrator.items.api import get_item_by_barcode
from cds_ils.migrator.patrons.api import get_user_by_legacy_id

loans_logger = logging.getLogger("loans_logger")


def validate_user(loan_record):
    """Validate loan patron."""
    user = get_user_by_legacy_id(loan_record["id_crcBORROWER"])
    if not user:
        # user was deleted, fallback to the AnonymousUser
        anonymous = current_app.config["ILS_PATRON_ANONYMOUS_CLASS"]
        return anonymous.id
    else:
        return user.pid


def validate_item(record):
    """Validate loan item."""
    return get_item_by_barcode(record["item_barcode"])


def validate_document_pid(record, item):
    """Validate loan document pid."""
    document_class = current_app_ils.document_record_cls
    # additional check if the loan refers to the same document
    # as it is already attached to the item
    document_pid = item.get("document_pid")

    document = document_class.get_record_by_pid(document_pid)
    if record["legacy_document_id"] is None:
        raise LoanMigrationError(
            "no document id for loan {}".format(record["legacy_id"])
        )
    if document.get("legacy_recid", None) != record["legacy_document_id"]:
        # this might happen when record merged or migrated,
        # the already migrated document should take precedence
        raise LoanMigrationError(
            "inconsistent document dependencies for loan {}".format(
                record["legacy_id"]
            ),
        )
    return document_pid


def provide_valid_loan_state_metadata(record, loan_dict):
    """Provide correct loan metadata."""
    if record["status"] == "on loan":
        loan_dict.update(
            dict(
                start_date=record["start_date"],
                end_date=record["end_date"],
                state="ITEM_ON_LOAN",
                transaction_date=record["start_date"],
            )
        )
    elif record["status"] == "returned":
        loan_dict.update(
            dict(
                transaction_date=record["returned_on"],
                start_date=record["start_date"],
                end_date=record["returned_on"],
                state="ITEM_RETURNED",
            )
        )
    # loan request
    elif record["status"] == "waiting" or record["status"] == "pending":
        loan_dict.update(
            dict(
                transaction_date=record["request_date"],
                request_start_date=record["period_of_interest_from"],
                request_expire_date=record["period_of_interest_to"],
                state="PENDING",
            )
        )
    # done loan requests became loans, and the rest we can ignore
    elif record["status"] in ["proposed", "cancelled", "done"]:
        return {}
    else:
        raise LoanMigrationError(
            "Unknown loan state for record {0}: {1}".format(
                record["legacy_id"], record["state"]
            )
        )
    return loan_dict


def validate_loan(new_loan_dict, record):
    """Validate loan."""
    if (
        new_loan_dict["patron_pid"] in ["-1", "-2"]
        and new_loan_dict["state"]
        in current_app.config["CIRCULATION_STATES_LOAN_ACTIVE"]
    ):
        raise LoanMigrationError(
            "Loan on item {0} has ongoing state "
            "while the patron is anonymous (ccid:{1})".format(
                record["item_barcode"], record["id_crcBORROWER"]
            )
        )


def import_loans_from_json(dump_file, raise_exceptions=False, rectype="loan"):
    """Imports loan objects from JSON."""
    (
        default_location_pid_value,
        _,
    ) = current_app_ils.get_default_location_pid

    with click.progressbar(json.load(dump_file)) as bar:
        for record in bar:
            click.echo('Importing loan "{0}"...'.format(record["legacy_id"]))

            try:
                patron_pid = validate_user(record)

                item = validate_item(record)
                if not item:
                    continue
                document_pid = validate_document_pid(record, item)

                # create a loan
                loan_dict = dict(
                    patron_pid=str(patron_pid),
                    transaction_location_pid=default_location_pid_value,
                    transaction_user_pid=str(SystemAgent.id),
                    document_pid=document_pid,
                    item_pid={
                        "value": item.pid.pid_value,
                        "type": item.pid.pid_type,
                    },
                )

                loan_dict = provide_valid_loan_state_metadata(
                    record, loan_dict
                )
                if not loan_dict:
                    continue
                validate_loan(loan_dict, record)

                import_record(
                    loan_dict,
                    rectype=rectype,
                    legacy_id_key=None,
                )
                db.session.commit()

            except Exception as exc:
                handler = json_records_exception_handlers.get(exc.__class__)
                if handler:
                    handler(
                        exc,
                        legacy_id=record["legacy_id"],
                        barcode=record["item_barcode"],
                        rectype=rectype,
                    )
                    if raise_exceptions:
                        raise exc
                else:
                    db.session.rollback()
                    if raise_exceptions:
                        raise exc
                    else:
                        continue
