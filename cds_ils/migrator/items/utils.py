# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator."""
from cds_ils.migrator.errors import ItemMigrationError


def clean_circulation_restriction(record):
    """Translates circulation restrictions of the item."""
    record["circulation_restriction"] = "NO_RESTRICTION"
    if "loan_period" in record:
        options = {"1 week": "ONE_WEEK", "4 weeks": "NO_RESTRICTION"}
        if record["loan_period"].lower() == "reference":
            record["status"] = "FOR_REFERENCE_ONLY"
        elif record["loan_period"] == "":
            record["circulation_restriction"] = "NO_RESTRICTION"
        else:
            try:
                record["circulation_restriction"] = options[
                    record["loan_period"]
                ]
            except KeyError:
                raise ItemMigrationError(
                    "Unknown circulation restriction (loan period) on "
                    "barcode {0}: {1}".format(
                        record["barcode"], record["loan_period"]
                    )
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


def clean_item_record(record):
    """Clean the item record object."""
    clean_circulation_restriction(record)
    clean_item_status(record)
    clean_description_field(record)
    record["shelf"] = record["location"]
    record["medium"] = "PAPER"  # requested as default value
    record["created_by"] = {"type": "script", "value": "migration"}
    del record["location"]
    del record["id_bibrec"]
    del record["id_crcLIBRARY"]
