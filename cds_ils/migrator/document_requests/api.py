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

from cds_ils.migrator.api import bulk_index_records, import_record, \
    model_provider_by_rectype
from cds_ils.migrator.utils import get_acq_ill_notes, get_patron_pid


def migrate_document_request(record):
    """Create a document request record for ILS."""
    state = "PENDING"
    new_docreq = dict(
        legacy_id=record["legacy_id"],
        patron_pid=get_patron_pid(record),
        title="Migrated record, no title provided",
        state=state,
        request_type="LOAN",
        medium="MIGRATED_UNKNOWN",
    )

    if record["status"] == "proposal-put aside":
        state = "REJECTED"
        reject_reason = record["library_notes"]
        new_docreq.update(state=state, reject_reason=reject_reason)

    note = get_acq_ill_notes(record)
    if note:
        new_docreq.update(note=note)

    return new_docreq


def import_document_requests_from_json(dump_file):
    """Imports document requests from JSON data files."""
    dump_file = dump_file[0]

    click.echo("Importing document requests ..")
    with click.progressbar(json.load(dump_file)) as input_data:
        ils_records = []
        for record in input_data:
            model, provider = model_provider_by_rectype("document-request")
            ils_record = import_record(
                migrate_document_request(record),
                model,
                provider,
                legacy_id_key="legacy_id",
            )
            ils_records.append(ils_record)
        db.session.commit()
    bulk_index_records(ils_records)
