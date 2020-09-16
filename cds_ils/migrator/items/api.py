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
from elasticsearch import VERSION as ES_VERSION
from elasticsearch_dsl import Q

from invenio_app_ils.items.api import Item
from invenio_app_ils.items.search import ItemSearch

from invenio_db import db

from cds_ils.migrator.api import model_provider_by_rectype, import_record
from cds_ils.migrator.documents.api import get_document_by_legacy_recid
from cds_ils.migrator.errors import (
    DocumentMigrationError,
    ItemMigrationError,
)
from cds_ils.migrator.internal_locations.api import \
    get_internal_location_by_legacy_recid
from cds_ils.migrator.utils import clean_item_record

lt_es7 = ES_VERSION[0] < 7
migrated_logger = logging.getLogger(
                            "migrated_documents"
                        )


def import_items_from_json(dump_file, include, rectype="item"):
    """Load items from json file."""
    dump_file = dump_file[0]
    model, provider = model_provider_by_rectype(rectype)

    include_ids = None if include is None else include.split(",")
    with click.progressbar(json.load(dump_file)) as bar:
        for record in bar:
            click.echo(
                'Importing item "{0}({1})"...'.format(
                    record["barcode"], rectype
                )
            )
            if include_ids is None or record["barcode"] in include_ids:

                int_loc_pid_value = get_internal_location_by_legacy_recid(
                    record["id_crcLIBRARY"]
                ).pid.pid_value

                record["internal_location_pid"] = int_loc_pid_value
                try:
                    record["document_pid"] = get_document_by_legacy_recid(
                        record["id_bibrec"]
                    ).pid.pid_value
                except DocumentMigrationError:
                    continue
                try:
                    clean_item_record(record)
                except ItemMigrationError as e:
                    click.secho(str(e), fg="red")
                    continue
                try:
                    # check if the item already there
                    item = get_item_by_barcode(record["barcode"])
                    if item:
                        click.secho(
                            "Item {0}) already exists with pid: {1}".format(
                                record["barcode"], item.pid
                            ),
                            fg="blue",
                        )
                        continue
                except ItemMigrationError:
                    record = import_record(
                        record, model, provider, legacy_id_key="barcode"
                    )
                try:
                    # without this script is very slow
                    db.session.commit()
                except Exception:
                    db.session.rollback()


def get_item_by_barcode(barcode):
    """Retrieve item object by barcode."""
    search = ItemSearch().query(
        "bool",
        filter=[
            Q("term", barcode=barcode),
        ],
    )
    result = search.execute()
    hits_total = result.hits.total if lt_es7 else result.hits.total.value
    if not result.hits or hits_total < 1:
        click.secho("no item found with barcode {}".format(barcode), fg="red")
        raise ItemMigrationError(
            "no item found with barcode {}".format(barcode)
        )
    elif hits_total > 1:
        raise ItemMigrationError(
            "found more than one item with barcode {}".format(barcode)
        )
    else:
        return Item.get_record_by_pid(result.hits[0].pid)


