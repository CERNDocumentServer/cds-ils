# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator API."""

import json

import click
from invenio_app_ils.internal_locations.api import InternalLocation
from invenio_app_ils.internal_locations.search import InternalLocationSearch
from invenio_app_ils.proxies import current_app_ils
from invenio_search.engine import dsl

from cds_ils.importer.vocabularies_validator import validator as vocabulary_validator
from cds_ils.migrator.api import import_record
from cds_ils.migrator.errors import ItemMigrationError
from cds_ils.migrator.providers.api import VOCABULARIES_FIELDS
from cds_ils.migrator.utils import bulk_index_records


def import_internal_locations_from_json(
    dump_file, include, rectype="internal_location"
):
    """Load parent records from file."""
    dump_file = dump_file[0]

    include_ids = None if include is None else include.split(",")
    location_pid_value, _ = current_app_ils.get_default_location_pid

    with click.progressbar(json.load(dump_file)) as bar:
        records = []
        for record in bar:
            click.echo(
                'Importing internal location "{0}({1})"...'.format(
                    record["legacy_ids"], rectype
                )
            )
            if include_ids is None or record["legacy_ids"] in include_ids:
                # remove the library type as it is not a part of the data model
                library_type = record.pop("type", None)
                if not isinstance(record["legacy_ids"], list):
                    record["legacy_ids"] = [str(record["legacy_ids"])]
                if library_type == "external":
                    # if the type is external => ILL Library
                    record["type"] = "LIBRARY"

                    vocabulary_validator.validate(VOCABULARIES_FIELDS, record)

                    record = import_record(
                        record,
                        rectype="provider",
                        legacy_id=record["legacy_ids"],
                        mint_legacy_pid=False,
                    )
                    records.append(record)
                else:
                    record["location_pid"] = location_pid_value
                    record = import_record(
                        record,
                        rectype="internal_location",
                        legacy_id=record["legacy_ids"],
                        mint_legacy_pid=False,
                    )
                    records.append(record)
    # Index all new internal location and libraries records
    bulk_index_records(records)


def get_internal_location_by_legacy_recid(legacy_recid):
    """Search for internal location by legacy id."""
    search = InternalLocationSearch().query(
        "bool", filter=[dsl.Q("term", legacy_ids=legacy_recid)]
    )
    result = search.execute()
    hits_total = result.hits.total.value
    if not result.hits or hits_total < 1:
        click.secho(
            "no internal location found with legacy id {}".format(legacy_recid),
            fg="red",
        )
        raise ItemMigrationError(
            "no internal location found with legacy id {}".format(legacy_recid)
        )
    elif hits_total > 1:
        raise ItemMigrationError(
            "found more than one internal location with legacy id {}".format(
                legacy_recid
            )
        )
    else:
        return InternalLocation.get_record_by_pid(result.hits[0].pid)
