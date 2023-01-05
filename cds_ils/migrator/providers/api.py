# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS provider migrator API.

Provider CDS fields:

legacy_id:
     name:
  address:
    email:
    phone:
    notes:
"""

import json

import click
from invenio_app_ils.providers.proxies import current_ils_prov
from invenio_db import db

from cds_ils.importer.vocabularies_validator import validator as vocabulary_validator
from cds_ils.migrator.api import import_record
from cds_ils.migrator.errors import ProviderError
from cds_ils.migrator.utils import bulk_index_records

ORIGINAL_WILEY_ID = 17
DEFAULT_WILEY = 333
WILEY_DE = 333
WILEY_UK = 444
WILEY_US = 555
WILEY_MAPPER = {
    "EUR": WILEY_DE,
    "GBP": WILEY_UK,
    "USD": WILEY_US,
}

VOCABULARIES_FIELDS = {
    "type": {
        "source": "json",
        "type": "provider_type",
    },
}


def get_provider_by_legacy_id(legacy_id, provider_type, grand_total=None):
    """Search for provider by legacy id."""
    # Check for Wiley vendor to split it depending on the currency
    if provider_type == "VENDOR" and legacy_id == ORIGINAL_WILEY_ID:
        if grand_total and grand_total["currency"]:
            legacy_id = WILEY_MAPPER.get(grand_total["currency"], DEFAULT_WILEY)
        else:
            legacy_id = DEFAULT_WILEY

    if provider_type:
        search = (
            current_ils_prov.provider_search_cls()
            .filter("term", legacy_ids=legacy_id)
            .filter("term", type=provider_type)
        )
    else:
        search = current_ils_prov.provider_search_cls().filter(
            "term", legacy_ids=legacy_id
        )
    result = search.execute()

    if len(result.hits) == 1:
        return current_ils_prov.provider_record_cls.get_record_by_pid(
            result.hits[0].pid
        )

    raise ProviderError(
        "Found {0} providers with legacy_id {1}".format(len(result.hits), legacy_id)
    )


def import_vendors_from_json(dump_file, rectype="provider"):
    """Imports vendors from JSON data files."""
    dump_file = dump_file[0]

    click.echo("Importing vendors ..")
    with click.progressbar(json.load(dump_file)) as input_data:
        ils_records = []
        for record in input_data:
            record["type"] = "VENDOR"
            # Legacy_ids in the .json file can be an array of strings or just
            # an integer, but we only accept an array of strings in the schema
            if not isinstance(record["legacy_ids"], list):
                record["legacy_ids"] = [str(record["legacy_ids"])]

            vocabulary_validator.validate(VOCABULARIES_FIELDS, record)

            ils_record = import_record(
                record,
                rectype=rectype,
                legacy_id=record["legacy_ids"],
                mint_legacy_pid=False,
            )
            ils_records.append(ils_record)
        db.session.commit()
    bulk_index_records(ils_records)
