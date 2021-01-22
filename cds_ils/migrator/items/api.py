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
from invenio_app_ils.proxies import current_app_ils
from invenio_db import db

from cds_ils.migrator.api import import_record
from cds_ils.migrator.errors import DocumentMigrationError, ItemMigrationError
from cds_ils.migrator.internal_locations.api import \
    get_internal_location_by_legacy_recid
from cds_ils.migrator.items.utils import clean_item_record, \
    find_document_for_item
from cds_ils.migrator.utils import model_provider_by_rectype

migrated_logger = logging.getLogger("migrated_records")
error_logger = logging.getLogger("records_errored")


def set_internal_location_pid(record):
    """Set internal location pid for item."""
    # find internal location
    int_loc_pid_value = get_internal_location_by_legacy_recid(
        record["id_crcLIBRARY"]
    ).pid.pid_value

    record["internal_location_pid"] = int_loc_pid_value


def set_document_pid(record):
    """Set document pid for item."""
    record["document_pid"] = None
    document = find_document_for_item(record)
    record["document_pid"] = document.pid.pid_value


def import_items_from_json(dump_file, rectype="item"):
    """Load items from json file."""
    model, provider = model_provider_by_rectype(rectype)
    with click.progressbar(json.load(dump_file)) as bar:
        error_logger.error(
            "ITEMS: PROCESSING {0}".format(
                dump_file
            )
        )
        migrated_logger.warning(
            "ITEMS: PROCESSING {0}".format(
                dump_file
            )
        )
        for record in bar:
            click.echo(
                'Importing item "{0}({1})"...'.format(
                    record["barcode"], rectype
                )
            )

            set_internal_location_pid(record)

            try:
                set_document_pid(record)
            except DocumentMigrationError:
                # there are items on the list which are not to be migrated
                # if no document found
                continue

            # clean the item JSON
            try:
                clean_item_record(record)
            except ItemMigrationError as e:
                click.secho(str(e), fg="red")
                error_logger.error(
                    "ITEM: {0} ERROR: {1}".format(record["barcode"], str(e))
                )
                continue

            # check if the item already there
            item = get_item_by_barcode(record["barcode"],
                                       raise_exception=False)
            if item:
                click.secho(
                    "Item {0}) already exists with pid: {1}".format(
                        record["barcode"], item.pid
                    ),
                    fg="blue",
                )
                continue
            else:
                try:
                    import_record(
                        record, model, provider, legacy_id_key="barcode"
                    )
                    db.session.commit()
                    migrated_logger.warning(
                        "ITEM: {0} OK".format(record["barcode"])
                    )
                except Exception as e:
                    error_logger.error(
                        "ITEM: {0} ERROR: {1}".format(
                            record["barcode"], str(e)
                        )
                    )
                    db.session.rollback()


def get_item_by_barcode(barcode, raise_exception=True):
    """Retrieve item object by barcode."""
    search = current_app_ils.item_search_cls().query(
        "bool",
        filter=[
            Q("term", barcode=barcode),
        ],
    )
    result = search.execute()
    hits_total = result.hits.total.value
    if not result.hits or hits_total < 1:
        click.secho("no item found with barcode {}".format(barcode), fg="red")
        if raise_exception:
            raise ItemMigrationError(
                "no item found with barcode {}".format(barcode)
            )
    elif hits_total > 1:
        raise ItemMigrationError(
            "found more than one item with barcode {}".format(barcode)
        )
    else:
        return current_app_ils.item_record_cls.get_record_by_pid(
            result.hits[0].pid
        )
