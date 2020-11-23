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

from cds_ils.migrator.api import import_record, model_provider_by_rectype
from cds_ils.migrator.errors import ItemMigrationError, LoanMigrationError
from cds_ils.migrator.items.api import get_item_by_barcode
from cds_ils.migrator.patrons.api import get_user_by_legacy_id

migrated_logger = logging.getLogger("migrated_records")
records_logger = logging.getLogger("records_errored")


def import_loans_from_json(dump_file):
    """Imports loan objects from JSON."""
    dump_file = dump_file[0]
    loans = []
    (
        default_location_pid_value,
        _,
    ) = current_app_ils.get_default_location_pid
    with click.progressbar(json.load(dump_file)) as bar:
        for record in bar:
            click.echo('Importing loan "{0}"...'.format(record["legacy_id"]))
            user = get_user_by_legacy_id(record["id_crcBORROWER"])
            if not user:
                # user was deleted, fallback to the AnonymousUser
                anonym = current_app.config["ILS_PATRON_ANONYMOUS_CLASS"]
                patron_pid = anonym.id
            else:
                patron_pid = user.pid
            try:
                item = get_item_by_barcode(record["item_barcode"])
            except ItemMigrationError:
                records_logger.error(
                    "LOAN: {0}, ERROR: barcode {1} not found.".format(
                        record["legacy_id"], record["item_barcode"]
                    )
                )
                continue
                # Todo uncomment when more data
                # raise LoanMigrationError(
                #    'no item found with the barcode {} for loan {}'.format(
                #        record['item_barcode'], record['legacy_id']))

            # additional check if the loan refers to the same document
            # as it is already attached to the item
            document_pid = item.get("document_pid")
            Document = current_app_ils.document_record_cls
            document = Document.get_record_by_pid(document_pid)
            if record["legacy_document_id"] is None:
                records_logger.error(
                    "LOAN: {0}, ERROR: document_legacy_recid {1} not found."
                    .format(
                        record["legacy_id"], record["legacy_document_id"]
                    )
                )
                raise LoanMigrationError(
                    "no document id for loan {}".format(record["legacy_id"])
                )
            if (
                document.get("legacy_recid", None)
                != record["legacy_document_id"]
            ):
                # this might happen when record merged or migrated,
                # the already migrated document should take precedence
                click.secho(
                    "inconsistent document dependencies for loan {}".format(
                        record["legacy_id"]
                    ),
                    fg="blue",
                )
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
            elif (
                record["status"] == "waiting" or record["status"] == "pending"
            ):
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
                continue
            else:
                raise LoanMigrationError(
                    "Unkown loan state for record {0}: {1}".format(
                        record["legacy_id"], record["state"]
                    )
                )
            model, provider = model_provider_by_rectype("loan")
            try:
                loan = import_record(
                    loan_dict, model, provider, legacy_id_key=None
                )
                db.session.commit()
                migrated_logger.warning(
                    "LOAN: {0} OK, new pid: {1}".format(
                        record["legacy_id"], loan["pid"]
                    )
                )
            except Exception as e:
                db.session.rollback()
                records_logger.error(
                    "LOAN: {0} ERROR: {1}".format(record["legacy_id"], str(e))
                )

    return loans
