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
from elasticsearch_dsl import Q
from invenio_app_ils.internal_locations.api import InternalLocation
from invenio_app_ils.internal_locations.search import InternalLocationSearch
from invenio_app_ils.proxies import current_app_ils

from cds_ils.migrator.api import bulk_index_records, import_record, \
    model_provider_by_rectype
from cds_ils.migrator.errors import ItemMigrationError

migrated_logger = logging.getLogger("migrated_documents")


def import_internal_locations_from_json(
    dump_file, include, rectype="internal_location"
):
    """Load parent records from file."""
    dump_file = dump_file[0]
    model, provider = model_provider_by_rectype(rectype)
    library_model, library_provider = model_provider_by_rectype("library")

    include_ids = None if include is None else include.split(",")

    (
        location_pid_value,
        _,
    ) = current_app_ils.get_default_location_pid

    with click.progressbar(json.load(dump_file)) as bar:
        records = []
        for record in bar:
            click.echo(
                'Importing internal location "{0}({1})"...'.format(
                    record["legacy_id"], rectype
                )
            )
            if include_ids is None or record["legacy_id"] in include_ids:
                # remove the library type as it is not a part of the data model
                library_type = record.pop("type", None)
                record["legacy_id"] = str(record["legacy_id"])
                if library_type == "external":
                    # if the type is external => ILL Library
                    record = import_record(
                        record,
                        library_model,
                        library_provider,
                        legacy_id_key="legacy_id",
                    )
                    records.append(record)
                else:

                    record["location_pid"] = location_pid_value
                    record = import_record(
                        record, model, provider, legacy_id_key="legacy_id"
                    )
                    records.append(record)
    # Index all new internal location and libraries records
    bulk_index_records(records)


def get_internal_location_by_legacy_recid(legacy_recid):
    """Search for internal location by legacy id."""
    search = InternalLocationSearch().query(
        "bool", filter=[Q("term", legacy_id=legacy_recid)]
    )
    result = search.execute()
    hits_total = result.hits.total.value
    if not result.hits or hits_total < 1:
        click.secho(
            "no internal location found with legacy id {}".format(
                legacy_recid
            ),
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
