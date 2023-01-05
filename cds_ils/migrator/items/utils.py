# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator."""
import logging

from flask import current_app
from invenio_app_ils.proxies import current_app_ils
from invenio_pidstore.errors import PIDDoesNotExistError

from cds_ils.literature.api import get_record_by_legacy_recid
from cds_ils.migrator.documents.api import get_document_by_barcode
from cds_ils.migrator.errors import DocumentMigrationError, ItemMigrationError

cli_logger = logging.getLogger("migrator")


def clean_circulation_restriction(record):
    """Translates circulation restrictions of the item."""
    record["circulation_restriction"] = "NO_RESTRICTION"
    intloc_record_cls = current_app_ils.internal_location_record_cls
    intloc = intloc_record_cls.get_record_by_pid(record["internal_location_pid"])
    if "loan_period" in record:
        options = {"1 week": "ONE_WEEK", "4 weeks": "NO_RESTRICTION"}
        # Only update status to "FOR_REFERENCE_ONLY" if item belongs to
        # LSL library (legacy_id = 9) and if item is not missing.
        if (
            "9" in intloc["legacy_ids"]
            and record["status"] != "MISSING"
            and record["loan_period"].lower() == "reference"
        ):
            record["status"] = "FOR_REFERENCE_ONLY"
        elif (
            record["loan_period"] == "" or record["loan_period"].lower() == "reference"
        ):
            record["circulation_restriction"] = "NO_RESTRICTION"
        else:
            try:
                record["circulation_restriction"] = options[record["loan_period"]]
            except KeyError:
                raise ItemMigrationError(
                    "Unknown circulation restriction (loan period) on "
                    "barcode {0}: {1}".format(record["barcode"], record["loan_period"])
                )
        del record["loan_period"]


def clean_item_status(record):
    """Translates item statuses."""
    # possible values:
    #   on shelf, missing, on loan, in binding, on order,
    #   out of print, not published, not arrived, under review
    options = {
        "on shelf": "CAN_CIRCULATE",
        "missing": "MISSING",
        "on loan": "CAN_CIRCULATE",
        "in binding": "IN_BINDING",
    }
    try:
        record["status"] = options[record["status"]]
    except KeyError:
        raise ItemMigrationError(
            "Unknown item status {0} on barcode {1}".format(
                record["status"], record["barcode"]
            )
        )


def clean_description_field(record):
    """Cleans the item description."""
    if record["description"] == "-" or record["description"] is None:
        del record["description"]


def find_document_for_item(item_json):
    """Returns the document from an item."""
    document = None
    document_cls = current_app_ils.document_record_cls
    legacy_pid_type = current_app.config["CDS_ILS_RECORD_LEGACY_PID_TYPE"]
    try:
        document = get_record_by_legacy_recid(
            document_cls, legacy_pid_type, item_json["id_bibrec"]
        )
    except PIDDoesNotExistError as e:
        try:
            document = get_document_by_barcode(item_json["barcode"])
        except DocumentMigrationError as e:
            pass

    if document is None:
        error_msg = (
            f"Document {item_json['id_bibrec']} not found"
            f" for barcode {item_json['barcode']}"
        )
        cli_logger.error(error_msg)
        raise ItemMigrationError(error_msg)
    return document


def clean_medium(record):
    """Translates the item medium."""
    document_cls = current_app_ils.document_record_cls
    document = document_cls.get_record_by_pid(record["document_pid"])

    if document.get("_migration", {}).get("has_medium", {}):
        for item in document["_migration"]["item_medium"]:
            if record["barcode"] == item["barcode"]:
                record["medium"] = item["medium"]
    medium = record.get("medium")
    if not medium:
        record["medium"] = "PAPER"  # requested as default value


def clean_item_record(record):
    """Clean the item record object."""
    # Attention! order of cleaning matters,
    # circulation restriction updates item status
    clean_item_status(record)
    clean_circulation_restriction(record)
    clean_description_field(record)
    clean_medium(record)
    record["shelf"] = record["location"]
    record["created_by"] = {"type": "script", "value": "migration"}
    record["legacy_library_id"] = str(record["id_crcLIBRARY"])
    record["legacy_id"] = ""
    del record["location"]
    del record["id_bibrec"]
    del record["id_crcLIBRARY"]
