# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator API."""
import logging
from copy import deepcopy

import click
from elasticsearch import VERSION as ES_VERSION
from elasticsearch_dsl import Q
from flask import current_app
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.series.api import Series
from invenio_app_ils.series.search import SeriesSearch

from cds_ils.migrator.errors import DocumentMigrationError, \
    MultipartMigrationError
from cds_ils.migrator.utils import pick

lt_es7 = ES_VERSION[0] < 7
migrated_logger = logging.getLogger("migrated_documents")
records_logger = logging.getLogger("records_errored")


def clean_document_json_for_multipart(json_record, include_keys=None):
    """Clean json to multipart form."""
    if not include_keys:
        include_keys = []
    cleaned_multipart_json = pick(
        json_record,
        "mode_of_issuance",
        "_migration",
        "physical_description",
        "identifiers",
        "languages",
        "internal_notes",
        "note",
        "title",
        "urls",
        *include_keys
    )
    cleaned_multipart_json["authors"] = [
        author["full_name"] for author in json_record.get("authors")
    ]
    return cleaned_multipart_json


def exclude_multipart_fields(json_record, exclude_keys=None):
    """Exclude multipart fields from document json."""
    cleaned = deepcopy(json_record)
    multipart_fields = ["mode_of_issuance"]
    if exclude_keys:
        multipart_fields += exclude_keys
    for field in multipart_fields:
        if field in cleaned:
            del cleaned[field]
    return cleaned


def get_multipart_by_multipart_id(multipart_id):
    """Search multiparts by its identifier."""
    series_search = current_app_ils.series_search_cls()
    series_cls = current_app_ils.series_record_cls
    # f.e. multipart id = vol234
    search = series_search.query(
        "match", _migration__multipart_id=multipart_id
    ).filter("match", mode_of_issuance="MULTIPART_MONOGRAPH")
    result = search.execute()
    hits_total = result.hits.total.value
    if hits_total == 1:
        return series_cls.get_record_by_pid(result.hits[0].pid)
    if hits_total == 0:
        click.secho(
            "no multipart found with id {}".format(multipart_id), fg="red"
        )
    else:
        raise MultipartMigrationError(
            "found more than one multipart id {}".format(multipart_id)
        )


def replace_fields_in_volume(document_json_template, volume_json, json_record):
    """Replace values of volume json template with new data."""
    # clean the template
    document_json_template["_migration"]["items"] = []
    document_json_template["_migration"]["legacy_recid"] = json_record[
        "legacy_recid"
    ]
    if "urls" in document_json_template:
        del document_json_template["urls"]
    if "identifiers" in document_json_template:
        del document_json_template["identifiers"]
    document_json_template["title"] = json_record.get("title")

    current_volume_index = volume_json.get("volume")
    volume_title = volume_json.get("title")

    # additional info for each volume
    volumes_items_list = json_record["_migration"]["items"]
    volumes_identifiers_list = json_record["_migration"]["volumes_identifiers"]
    volumes_urls_list = json_record["_migration"]["volumes_urls"]

    if volume_title:
        document_json_template["title"] = volume_title

    # split items per volume
    volume_items = [
        item
        for item in volumes_items_list
        if item.get("volume") == current_volume_index
    ]
    if volume_items:
        document_json_template["_migration"]["items"] = volume_items

    # split urls per volume
    volume_urls = [
        url
        for url in volumes_urls_list
        if url.get("volume") == current_volume_index
    ]
    if volume_urls:
        document_json_template["urls"] = volume_urls

    # split identifiers per volume
    volume_identifiers = [
        identifier
        for identifier in volumes_identifiers_list
        if identifier.get("volume") == current_volume_index
    ]
    if volume_identifiers:
        document_json_template["identifiers"] = volume_identifiers


def get_serials_by_child_recid(recid):
    """Search serials by children recid."""
    series_search = current_app_ils.series_search_cls()
    series_class = current_app_ils.series_record_cls
    search = series_search.query(
        "bool",
        filter=[
            Q("term", mode_of_issuance="SERIAL"),
            Q("term", _migration__children=recid),
        ],
    )
    for hit in search.scan():
        yield series_class.get_record_by_pid(hit.pid)


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
        document_cls = current_app_ils.document_record_cls

        relations = serial.relations.get().get("serial", [])
        if len(recids) != len(relations):
            click.echo(
                "[Serial {}] Incorrect number of children: {} "
                "(expected {})".format(
                    serial["pid"], len(relations), len(recids)
                )
            )
        for relation in relations:

            child = document_cls.get_record_by_pid(
                relation["pid"], pid_type=relation["pid_type"]
            )
            if "legacy_recid" in child and child["legacy_recid"] not in recids:
                click.echo(
                    "[Serial {}] Unexpected child with legacy "
                    "recid: {}".format(serial["pid"], child["legacy_recid"])
                )

    titles = set()
    series_search = current_app_ils.series_search_cls()

    search = series_search.filter("term", mode_of_issuance="SERIAL")
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
        document_cls = current_app_ils.document_record_cls
        relations = multipart.relations.get().get("multipart_monograph", [])
        titles = [volume["title"] for volume in volumes if "title" in volume]
        count = len(set(v["volume"] for v in volumes))
        if count != len(relations):
            click.echo(
                "[Multipart {}] Incorrect number of volumes: {} "
                "(expected {})".format(multipart["pid"], len(relations), count)
            )
        for relation in relations:

            child = document_cls.get_record_by_pid(
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
