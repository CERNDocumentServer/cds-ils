# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Migrator Records utils."""

import datetime
from contextlib import contextmanager

import click
from flask import current_app
from invenio_accounts.models import User
from invenio_app_ils.acquisition.api import Order, OrderIdProvider
from invenio_app_ils.circulation.api import IlsCirculationLoanIdProvider
from invenio_app_ils.document_requests.api import (
    DocumentRequest,
    DocumentRequestIdProvider,
)
from invenio_app_ils.documents.api import DocumentIdProvider
from invenio_app_ils.ill.api import BorrowingRequest, BorrowingRequestIdProvider
from invenio_app_ils.internal_locations.api import InternalLocationIdProvider
from invenio_app_ils.items.api import ItemIdProvider
from invenio_app_ils.providers.api import Provider, ProviderIdProvider
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.series.api import SeriesIdProvider
from invenio_base.app import create_cli
from invenio_circulation.proxies import current_circulation
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.errors import PIDDoesNotExistError

from cds_ils.literature.api import get_record_by_legacy_recid
from cds_ils.migrator.constants import MIGRATION_DOCUMENT_PID
from cds_ils.migrator.errors import AcqOrderError
from cds_ils.migrator.patrons.api import get_user_by_legacy_id


def pick(obj, *keys):
    """Pick and return only the specified keys."""
    return {k: obj.get(k) for k in obj.keys() if k in keys}


@contextmanager
def commit():
    """Commit transaction or rollback in case of an exception."""
    try:
        yield
        db.session.commit()
    except Exception:
        print("Rolling back changes...")
        db.session.rollback()
        raise


def reindex_pidtype(pid_type):
    """Reindex records with the specified pid_type."""
    click.echo('Indexing pid type "{}"...'.format(pid_type))
    cli = create_cli()
    runner = current_app.test_cli_runner()
    runner.invoke(
        cli,
        "index reindex --pid-type {} --yes-i-know".format(pid_type),
        catch_exceptions=True,
    )
    runner.invoke(cli, "index run", catch_exceptions=True)
    click.echo("Indexing completed!")


def bulk_index_records(records):
    """Bulk index a list of records."""
    indexer = RecordIndexer()

    click.echo("Bulk indexing {} records...".format(len(records)))
    indexer.bulk_index([str(r.id) for r in records])
    indexer.process_bulk_queue()
    click.echo("Indexing completed!")


def model_provider_by_rectype(rectype):
    """Return the correct model and PID provider based on the rectype."""
    if rectype in ("serial", "multipart", "journal"):
        series_class = current_app_ils.series_record_cls
        return series_class, SeriesIdProvider
    elif rectype == "document":
        document_class = current_app_ils.document_record_cls
        return document_class, DocumentIdProvider
    elif rectype == "internal_location":
        internal_location_class = current_app_ils.internal_location_record_cls
        return internal_location_class, InternalLocationIdProvider
    elif rectype == "item":
        item_class = current_app_ils.item_record_cls
        return item_class, ItemIdProvider
    elif rectype == "loan":
        loan_class = current_circulation.loan_record_cls
        return loan_class, IlsCirculationLoanIdProvider
    elif rectype == "provider":
        return Provider, ProviderIdProvider
    elif rectype == "borrowing-request":
        return BorrowingRequest, BorrowingRequestIdProvider
    elif rectype == "acq-order":
        return Order, OrderIdProvider
    elif rectype == "document-request":
        return DocumentRequest, DocumentRequestIdProvider
    raise ValueError("Unknown rectype: {}".format(rectype))


def get_legacy_pid_type_by_provider(provider):
    """Get mintable legacy pid type based on provider pid type."""
    config = current_app.config
    mintable_pids_map = {
        "docid": config["CDS_ILS_RECORD_LEGACY_PID_TYPE"],
        "serid": config["CDS_ILS_SERIES_LEGACY_PID_TYPE"],
        "pitmid": config["CDS_ILS_ITEM_LEGACY_PID_TYPE"],
        "illbid": config["CDS_ILS_BORROWING_REQ_LEGACY_PID_TYPE"],
        "acqoid": config["CDS_ILS_ACQ_ORDER_LEGACY_PID_TYPE"],
        "loanid": config["CDS_ILS_LOAN_LEGACY_PID_TYPE"],
    }
    return mintable_pids_map[provider.pid_type]


def clean_created_by_field(record):
    """Clean the created by field for documents."""
    if "created_by" not in record:
        record["created_by"] = {"type": "script", "value": "migration"}
        return record
    if "_email" in record["created_by"]:
        patron = User.query.filter_by(
            email=record["created_by"]["_email"]
        ).one_or_none()
        if patron:
            patron_pid = patron.get_id()
            record["created_by"] = {"type": "user_id", "value": patron_pid}
        else:
            record["created_by"] = {"type": "user_id", "value": "anonymous"}
    elif record["created_by"]["type"] == "batchuploader":
        record["created_by"] = {"type": "script", "value": "batchuploader"}
    else:
        record["created_by"] = {"type": "script", "value": "migration"}

    return record


def get_acq_ill_notes(record):
    """Extract notes for acquisition and ILL records."""
    # NOTE: library notes are usually empty dict string field '{}'
    result = ""

    request_type = record.get("request_type")
    if request_type:
        result += "request type: {0}\n\n".format(request_type)

    due_date = record.get("due_date")
    if due_date:
        result += "due date: {0}\n\n".format(due_date)

    return_date = record.get("return_date")
    if return_date:
        result += "return date: {0}\n\n".format(return_date)

    cost = record.get("cost")
    if cost:
        result += "cost: {0}\n\n".format(cost)

    item_info = record.get("item_info")
    if item_info:
        result += "item info: {0}\n\n".format(item_info.strip())

    comments = record.get("borrower_comments")
    if comments:
        result += "borrower comments: {0}\n\n".format(comments.strip())

    notes = record.get("library_notes")
    if not notes:
        return result

    result += "library notes: {0}\n".format(notes.strip())

    try:
        result = (
            # any encoding supporting printable ASCII would work e.g. utf-8
            result.encode("ascii")
            # unescape the string
            .decode("unicode-escape")
            # latin-1 also works
            .encode("iso-8859-1").decode("utf-8")
        )
    except UnicodeEncodeError:
        # result contains unicode chars that can't be ascii encoded
        pass
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


def get_date(value):
    """Strips time and validates that string can be converted to date."""
    date_only = value.split("T")[0]
    datetime.datetime.strptime(date_only, "%Y-%m-%d")
    return date_only


def add_cover_metadata(json_data):
    """Add first ISBN as to cover metadata."""
    isbn_list = [
        identifier
        for identifier in json_data.get("identifiers", [])
        if identifier["scheme"] == "ISBN"
    ]
    if isbn_list:
        json_data["cover_metadata"] = {"ISBN": isbn_list[0]["value"]}


def get_item_info(record):
    """Get dict out of item info field for Ills and orders.

    item_info: {
    'publisher': '',
    'isbn': '',
    'title': '',
    'authors': '',
    'edition': '',
    'place': '',
    'year': ''
    'recid': ''
    }
    """
    # DO NOT use at home
    item_info = eval(record.get("item_info"))
    return item_info


def find_correct_document_pid(record):
    """Try to attach document_pid or fall back to default."""
    document_cls = current_app_ils.document_record_cls
    legacy_pid_type = current_app.config["CDS_ILS_RECORD_LEGACY_PID_TYPE"]
    item_info = get_item_info(record)
    document_legacy_recid = item_info.get("recid")
    if document_legacy_recid:
        try:
            document = get_record_by_legacy_recid(
                document_cls, legacy_pid_type, document_legacy_recid
            )
            document_pid = document["pid"]
        except PIDDoesNotExistError as e:
            document_pid = MIGRATION_DOCUMENT_PID
    else:
        document_pid = MIGRATION_DOCUMENT_PID

    return document_pid
