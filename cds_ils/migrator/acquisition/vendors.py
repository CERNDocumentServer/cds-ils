# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS acquisition vendor migrator API.

Vendor CDS fields:

legacy_id:
     name:
  address:
    email:
    phone:
    notes:
"""

import json

import click
from elasticsearch_dsl import Q
from invenio_app_ils.acquisition.search import VendorSearch
from invenio_db import db

from cds_ils.migrator.api import bulk_index_records, import_record, \
    model_provider_by_rectype
from cds_ils.migrator.errors import VendorError


def get_vendor_pid_by_legacy_id(legacy_id):
    """Search for vendor by legacy id."""
    # NOTE: in case it is legacy_id == "0" return the dummy vendor
    search = VendorSearch().filter("term", legacy_id=legacy_id)
    result = search.execute()

    if len(result.hits) == 1:
        return result.hits[0].pid

    raise VendorError(
        "Found {0} vendors with legacy_id {1}".format(
            len(result.hits), legacy_id
        )
    )


def import_vendors_from_json(dump_file, include=None):
    """Imports vendors from JSON data files."""
    dump_file = dump_file[0]
    model, provider = model_provider_by_rectype("vendor")
    include_ids = None if include is None else include.split(",")

    click.echo("Importing vendors ..")
    with click.progressbar(json.load(dump_file)) as input_data:
        ils_records = []
        for record in input_data:
            if not (include_ids is None or record["legacy_id"] in include_ids):
                continue

            ils_record = import_record(
                record,
                model,
                provider,
                legacy_id_key="legacy_id",
            )
            ils_records.append(ils_record)
            ils_record.commit()
        db.session.commit()
    bulk_index_records(ils_records)
