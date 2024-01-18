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
from invenio_app_ils.proxies import current_app_ils
from invenio_db import db
from invenio_search.engine import dsl

from cds_ils.importer.vocabularies_validator import validator as vocabulary_validator
from cds_ils.migrator.api import import_record
from cds_ils.migrator.errors import ItemMigrationError
from cds_ils.migrator.handlers import json_records_exception_handlers
from cds_ils.migrator.internal_locations.api import (
    get_internal_location_by_legacy_recid,
)
from cds_ils.migrator.items.utils import clean_item_record, find_document_for_item

items_logger = logging.getLogger("items_logger")

VOCABULARIES_FIELDS = {
    "medium": {
        "source": "json",
        "type": "item_medium",
    },
    "price": {
        "currency": {
            "source": "json",
            "type": "currencies",
        },
    },
}


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
    with click.progressbar(json.load(dump_file)) as bar:
        for record in bar:
            log_extra = dict(
                document_legacy_recid=record["id_bibrec"],
            )

            click.echo(
                'Importing item "{0}({1})"...'.format(record["barcode"], rectype)
            )
            try:
                set_internal_location_pid(record)
                set_document_pid(record)
                # clean the item JSON
                clean_item_record(record)

                vocabulary_validator.validate(VOCABULARIES_FIELDS, record)

                import_record(
                    record,
                    rectype=rectype,
                    legacy_id=record["barcode"],
                    log_extra=log_extra,
                )
            except Exception as exc:
                handler = json_records_exception_handlers.get(exc.__class__)
                if handler:
                    handler(
                        exc,
                        document_legacy_recid=record.get("id_bibrec")
                        or record.get("document_pid"),
                        legacy_id=record["barcode"],
                        rectype=rectype,
                    ),
                else:
                    db.session.rollback()
                    raise exc


def get_item_by_barcode(barcode, raise_exception=True):
    """Retrieve item object by barcode."""
    search = current_app_ils.item_search_cls().query(
        "bool",
        filter=[
            dsl.Q("term", barcode=barcode),
        ],
    )
    result = search.execute()
    hits_total = result.hits.total.value
    if not result.hits or hits_total < 1:
        click.secho("no item found with barcode {}".format(barcode), fg="red")
        if raise_exception:
            raise ItemMigrationError("no item found with barcode {}".format(barcode))
    elif hits_total > 1:
        raise ItemMigrationError(
            "found more than one item with barcode {}".format(barcode)
        )
    else:
        return current_app_ils.item_record_cls.get_record_by_pid(result.hits[0].pid)
