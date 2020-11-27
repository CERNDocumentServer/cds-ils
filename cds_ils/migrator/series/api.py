# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator API."""

import logging
import uuid

import click
from elasticsearch import VERSION as ES_VERSION
from elasticsearch_dsl import Q
from flask import current_app
from invenio_app_ils.documents.api import Document, DocumentIdProvider
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.series.api import Series
from invenio_app_ils.series.search import SeriesSearch

from cds_ils.migrator.errors import DocumentMigrationError, \
    MultipartMigrationError

lt_es7 = ES_VERSION[0] < 7
migrated_logger = logging.getLogger("migrated_documents")


def get_multipart_by_legacy_recid(legacy_recid):
    """Search series by its legacy recid."""
    series_search = current_app_ils.series_search_cls()
    series_class = current_app_ils.series_record_cls
    search = series_search.query(
        "bool", filter=[Q("term", legacy_recid=legacy_recid)]
    )
    result = search.execute()
    hits_total = result.hits.total.value

    if hits_total == 1:
        click.secho(
            "! series found with legacy recid {}".format(legacy_recid),
            fg="green",
        )
        return series_class.get_record_by_pid(result.hits[0].pid)

    elif hits_total == 0:
        click.secho(
            "no series found with legacy recid {}".format(legacy_recid),
            fg="red",
        )
        raise MultipartMigrationError(
            "no series found with legacy recid {}".format(legacy_recid)
        )
    else:
        click.secho(
            "found more than one series with recid {}".format(legacy_recid),
            fg="red",
        )
        raise MultipartMigrationError(
            "found more than one series with recid {}".format(legacy_recid)
        )


def create_multipart_volumes(pid, multipart_legacy_recid, migration_volumes):
    """Create multipart volume documents."""
    volumes = {}
    # Combine all volume data by volume number
    click.echo("Creating volume for {}...".format(multipart_legacy_recid))
    for obj in migration_volumes:
        volume_number = obj["volume"]
        if volume_number not in volumes:
            volumes[volume_number] = {}
        volume = volumes[volume_number]
        for key in obj:
            if key != "volume":
                if key in volume:
                    raise KeyError(
                        'Duplicate key "{}" for multipart {}'.format(
                            key, multipart_legacy_recid
                        )
                    )
                volume[key] = obj[key]

    volume_numbers = iter(sorted(volumes.keys()))

    # Re-use the current record for the first volume
    # TODO review this - there are more cases of multiparts
    first_volume = next(volume_numbers)
    first = Document.get_record_by_pid(pid)
    if "title" in volumes[first_volume]:
        first["title"] = volumes[first_volume]["title"]
        first["volume"] = first_volume
    first["_migration"]["multipart_legacy_recid"] = multipart_legacy_recid
    # to be tested
    if "legacy_recid" in first:
        del first["legacy_recid"]

    # Create new records for the rest
    for number in volume_numbers:
        temp = first.copy()
        temp["title"] = volumes[number]["title"]
        temp["volume"] = number
        record_uuid = uuid.uuid4()
        provider = DocumentIdProvider.create(
            object_type="rec", object_uuid=record_uuid
        )
        temp["pid"] = provider.pid.pid_value
        record = Document.create(temp, record_uuid)
        record.commit()
        yield record


def get_serials_by_child_recid(recid):
    """Search serials by children recid."""
    search = SeriesSearch().query(
        "bool",
        filter=[
            Q("term", mode_of_issuance="SERIAL"),
            Q("term", _migration__children=recid),
        ],
    )
    for hit in search.scan():
        yield Series.get_record_by_pid(hit.pid)


def get_migrated_volume_by_serial_title(record, title):
    """Get volume number by serial title."""
    for serial in record["_migration"]["serials"]:
        if serial["title"] == title:
            return serial.get("volume", None)
    raise DocumentMigrationError(
        'Unable to find volume number in record {} by title "{}"'.format(
            record["pid"], title
        )
    )


def validate_serial_records():
    """Validate that serials were migrated successfully.

    Performs the following checks:
    * Find duplicate serials
    * Ensure all children of migrated serials were migrated
    """

    def validate_serial_relation(serial, recids):
        relations = serial.relations.get().get("serial", [])
        if len(recids) != len(relations):
            click.echo(
                "[Serial {}] Incorrect number of children: {} "
                "(expected {})".format(
                    serial["pid"], len(relations), len(recids)
                )
            )
        for relation in relations:
            Document = current_app_ils.document_record_cls
            child = Document.get_record_by_pid(
                relation["pid"], pid_type=relation["pid_type"]
            )
            if "legacy_recid" in child and child["legacy_recid"] not in recids:
                click.echo(
                    "[Serial {}] Unexpected child with legacy "
                    "recid: {}".format(serial["pid"], child["legacy_recid"])
                )

    titles = set()
    search = SeriesSearch().filter("term", mode_of_issuance="SERIAL")
    for serial_hit in search.scan():
        # Store titles and check for duplicates
        if "title" in serial_hit:
            title = serial_hit.title
            if title in titles:
                current_app.logger.warning(
                    'Serial title "{}" already exists'.format(title)
                )
            else:
                titles.add(title)
        # Check if any children are missing
        children = serial_hit._migration.children
        serial = Series.get_record_by_pid(serial_hit.pid)
        validate_serial_relation(serial, children)

    click.echo("Serial validation check done!")


def validate_multipart_records():
    """Validate that multiparts were migrated successfully.

    Performs the following checks:
    * Ensure all volumes of migrated multiparts were migrated
    """

    def validate_multipart_relation(multipart, volumes):
        relations = multipart.relations.get().get("multipart_monograph", [])
        titles = [volume["title"] for volume in volumes if "title" in volume]
        count = len(set(v["volume"] for v in volumes))
        if count != len(relations):
            click.echo(
                "[Multipart {}] Incorrect number of volumes: {} "
                "(expected {})".format(multipart["pid"], len(relations), count)
            )
        for relation in relations:
            Document = current_app_ils.document_record_cls
            child = Document.get_record_by_pid(
                relation["pid"], pid_type=relation["pid_type"]
            )
            if child["title"] not in titles:
                click.echo(
                    '[Multipart {}] Title "{}" does not exist in '
                    "migration data".format(multipart["pid"], child["title"])
                )

    search = SeriesSearch().filter(
        "term", mode_of_issuance="MULTIPART_MONOGRAPH"
    )
    for multipart_hit in search.scan():
        # Check if any child is missing
        if "volumes" in multipart_hit._migration:
            volumes = multipart_hit._migration.volumes
            multipart = Series.get_record_by_pid(multipart_hit.pid)
            validate_multipart_relation(multipart, volumes)

    click.echo("Multipart validation check done!")
