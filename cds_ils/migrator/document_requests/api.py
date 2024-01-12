# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS document requests migrator API."""

import json

import click
from invenio_db import db

from cds_ils.importer.vocabularies_validator import validator as vocabulary_validator
from cds_ils.migrator.api import import_record
from cds_ils.migrator.utils import bulk_index_records, get_acq_ill_notes, get_patron_pid

VOCABULARIES_FIELDS = {
    "medium": {
        "source": "json",
        "type": "doc_req_medium",
    },
    "payment_method": {
        "source": "json",
        "type": "doc_req_payment_method",
    },
    "request_type": {
        "source": "json",
        "type": "doc_req_type",
    },
}


def migrate_document_request(record):
    """Create a document request record for ILS."""
    state = "PENDING"
    new_docreq = dict(
        legacy_id=record["legacy_id"],
        patron_pid=get_patron_pid(record),
        title="Migrated record, no title provided",
        state=state,
        request_type="LOAN",
        medium="PAPER",
    )

    if record["status"] == "proposal-put aside":
        state = "DECLINED"
        new_docreq.update(state=state, decline_reason="OTHER")

    note = get_acq_ill_notes(record)
    if note:
        new_docreq.update(note=note)

    vocabulary_validator.validate(VOCABULARIES_FIELDS, new_docreq)

    return new_docreq


def import_document_requests_from_json(dump_file, rectype="document-request"):
    """Imports document requests from JSON data files."""
    click.echo("Importing document requests ..")
    with click.progressbar(json.load(dump_file)) as input_data:
        ils_records = []
        for record in input_data:
            ils_record = import_record(
                migrate_document_request(record),
                rectype=rectype,
                legacy_id=record["legacy_id"],
                mint_legacy_pid=False,
            )
            ils_records.append(ils_record)
        db.session.commit()
    bulk_index_records(ils_records)
