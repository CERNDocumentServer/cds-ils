# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Migrator Records utils."""
import datetime
import json
import logging
import uuid

from flask import current_app
from invenio_accounts.models import User
from invenio_app_ils.acquisition.api import VENDOR_PID_TYPE
from invenio_app_ils.acquisition.proxies import current_ils_acq
from invenio_app_ils.documents.api import DOCUMENT_PID_TYPE
from invenio_app_ils.ill.api import LIBRARY_PID_TYPE
from invenio_app_ils.ill.proxies import current_ils_ill
from invenio_app_ils.proxies import current_app_ils
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from cds_ils.cli import mint_record_pid
from cds_ils.migrator.errors import ItemMigrationError
from cds_ils.migrator.patrons.api import get_user_by_legacy_id

logger = logging.getLogger("migrator")


def process_fireroles(fireroles):
    """Extract firerole definitions."""
    rigths = set()
    for firerole in fireroles:
        for (allow, not_, field, expressions_list) in firerole[1]:
            if not allow:
                current_app.logger.warning(
                    "Not possible to migrate deny rules: {0}.".format(
                        expressions_list
                    )
                )
                continue
            if not_:
                current_app.logger.warning(
                    "Not possible to migrate not rules: {0}.".format(
                        expressions_list
                    )
                )
                continue
            if field in ("remote_ip", "until", "from"):
                current_app.logger.warning(
                    "Not possible to migrate {0} rule: {1}.".format(
                        field, expressions_list
                    )
                )
                continue
            # We only deal with allow group rules
            for reg, expr in expressions_list:
                if reg:
                    current_app.logger.warning(
                        "Not possible to migrate groups based on regular"
                        " expressions: {0}.".format(expr)
                    )
                    continue
                clean_name = (
                    expr[: -len(" [CERN]")].lower().strip().replace(" ", "-")
                )
                rigths.add("{0}@cern.ch".format(clean_name))
    return rigths


def update_access(data, *access):
    """Merge access rights information.

    :params data: current JSON structure with metadata and potentially an
        `_access` key.
    :param *access: List of dictionaries to merge to the original data, each of
        them in the form `action: []`.
    """
    current_rules = data.get("_access", {})
    for a in access:
        for k, v in a.items():
            current_x_rules = set(current_rules.get(k, []))
            current_x_rules.update(v)
            current_rules[k] = list(current_x_rules)

    data["_access"] = current_rules


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
        "FOR_REFERENCE_ONLY": "CAN_CIRCULATE",
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
    del record["location"]
    del record["id_bibrec"]
    del record["id_crcLIBRARY"]


def clean_created_by_field(record):
    """Clean the created by field for documents."""
    if "_email" in record["created_by"]:
        patron = User.query.filter_by(
            email=record["created_by"]["_email"]
        ).one_or_none()
        if patron:
            patron_pid = patron.get_id()
            record["created_by"] = {"type": "user_id", "value": patron_pid}
        else:
            record["created_by"] = {"type": "user_id", "value": "anonymous"}
        del record["created_by"]["_email"]
    elif record["created_by"]["type"] == "batchuploader":
        record["created_by"] = {"type": "script", "value": "batchuploader"}
    else:
        record["created_by"] = {"type": "script", "value": "migration"}

    return record


def get_acq_ill_notes(record):
    """Extract notes for acquisition and ILL records."""
    # NOTE: library notes are usually empty dict stringified '{}'
    result = ""
    cost = record.get("cost")
    if cost:
        result += "cost: {0}\n\n".format(cost)

    item_info = record.get("item_info")
    if item_info:
        result = "item info: {0}\n\n".format(item_info.strip())

    comments = record.get("borrower_comments")
    if comments:
        result = "borrower comments: {0}\n\n".format(comments.strip())

    notes = record.get("library_notes")
    if not notes:
        return result

    result += "library notes: {0}\n".format(notes.strip())
    return result


def get_cost(record):
    """Parse CDS cost string to extract currency and value."""
    SUPPORTED_CURRENCIES = ["EUR", "USD", "GBP", "CHF", "YEN"]
    # NOTE: We will try to extract and migrate only the most common case, which
    # comes to the form "EUR 88.40". If it comes in any other form will
    # store it in notes.

    try:
        [currency, value] = record.get("cost").split(" ")
        if currency.upper() in SUPPORTED_CURRENCIES:
            return {"currency": currency.upper(), "value": float(value)}
    except ValueError:
        # We don't care, we will check again at get_acq_ill_notes()
        pass


def get_patron_pid(record):
    """Get patron_pid from existing users."""
    user = get_user_by_legacy_id(record["id_crcBORROWER"])
    if not user:
        # user was deleted, fallback to the AnonymousUser
        anonym = current_app.config["ILS_PATRON_ANONYMOUS_CLASS"]()
        patron_pid = str(anonym.id)
    else:
        patron_pid = user.pid
    return str(patron_pid)


MIGRATION_DOCUMENT_PID = "DOCPID-44444"
MIGRATION_LIBRARY_PID = "LIBPID-44444"
MIGRATION_VENDOR_PID = "VENPID-44444"


def mint_migration_records(pid_type, pid_field, data):
    """Minter for migration records."""
    record_uuid = uuid.uuid4()
    PersistentIdentifier.create(
        pid_type=pid_type,
        pid_value=data[pid_field],
        object_type="rec",
        object_uuid=record_uuid,
        status=PIDStatus.REGISTERED,
    )
    return record_uuid


def get_migration_document_pid():
    """Get the PID of the dedicated migration document."""
    return current_app_ils.document_record_cls.get_record_by_pid(
        MIGRATION_DOCUMENT_PID
    ).pid.pid_value


def create_document():
    """Create migration document."""
    data = {
        "pid": MIGRATION_DOCUMENT_PID,
        "title": "Migrated Unknown Document",
        "authors": [{"full_name": "Legacy CDS service"}],
        "publication_year": "2020",
        "document_type": "BOOK",
        "restricted": True,
        "notes": """This document is used whenever we document information
        is required and not provided, in order to migrate data from CDS.
        """
    }
    record_uuid = mint_migration_records(DOCUMENT_PID_TYPE, "pid", data)
    doc = current_app_ils.document_record_cls.create(data, record_uuid)
    db.session.commit()
    current_app_ils.document_indexer.index(doc)
    return doc


def create_library():
    """Create migration library."""
    data = {
        "pid": MIGRATION_LIBRARY_PID,
        "name": "Migrated Unknown Library",
        "legacy_id": "0",
        "notes": """This Library is used whenever we had lirary with
        legacy ID 0 in CDS Acquisition and ILL data.
        """
    }

    record_uuid = mint_migration_records(LIBRARY_PID_TYPE, "pid", data)
    library = current_ils_ill.library_record_cls.create(data, record_uuid)
    db.session.commit()
    current_ils_ill.library_indexer.index(library)
    return library


def create_vendor():
    """Create migration vendor."""
    data = {
        "pid": MIGRATION_VENDOR_PID,
        "name": "Migrated Unknown Vendor",
        "legacy_id": "0",
        "notes": """This Vendor is used whenever we had vendor ID 0
        in CDS Acquisition and ILL data.
        """
    }

    record_uuid = mint_migration_records(VENDOR_PID_TYPE, "pid", data)
    vendor = current_ils_acq.vendor_record_cls.create(data, record_uuid)
    db.session.commit()
    current_ils_acq.vendor_indexer.index(vendor)
    return vendor


def create_migration_records():
    """Create migration records."""
    create_document()
    create_vendor()
    create_library()


def get_date(value):
    """Strips time and validates that string can be converted to date."""
    date_only = value.split("T")[0]
    try:
        datetime.datetime.strptime(date_only, "%Y-%m-%d")
    except ValueError:
        logger.error("{0} is not a valid date".format(date_only))
    return date_only
