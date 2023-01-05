# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator."""

from flask import current_app
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.records_relations.indexer import RecordRelationIndexer
from invenio_app_ils.relations.api import MULTIPART_MONOGRAPH_RELATION
from invenio_db import db
from invenio_pidstore.errors import PIDDoesNotExistError

from cds_ils.importer.errors import ManualImportRequired
from cds_ils.importer.providers.cds.utils import add_cds_url
from cds_ils.literature.api import get_record_by_legacy_recid
from cds_ils.migrator.api import import_record
from cds_ils.migrator.errors import MultipartMigrationError
from cds_ils.migrator.relations.api import create_parent_child_relation
from cds_ils.migrator.series.api import (
    clean_document_json_for_multipart,
    exclude_multipart_fields,
    get_multipart_by_multipart_id,
    replace_fields_in_volume,
)


def import_multivolume(json_record):
    """Import multivolume type of multipart."""
    document_indexer = current_app_ils.document_indexer
    series_indexer = current_app_ils.series_indexer
    series_cls = current_app_ils.series_record_cls

    legacy_recid = json_record["legacy_recid"]

    # build multipart dict - leave the legacy_recid attached
    multipart_json = clean_document_json_for_multipart(
        json_record,
        include_keys=[
            "legacy_recid",
            "alternative_titles",
            "publication_year",
            "identifiers",
        ],
    )

    # prepare json for each volume
    document_json_template = exclude_multipart_fields(
        json_record, exclude_keys=["legacy_recid", "alternative_titles"]
    )

    volume_list = json_record["_migration"]["volumes"]

    try:
        legacy_pid_type = current_app.config["CDS_ILS_SERIES_LEGACY_PID_TYPE"]
        get_record_by_legacy_recid(series_cls, legacy_pid_type, legacy_recid)
        raise MultipartMigrationError(
            f"Multipart {legacy_recid} was already processed. Aborting."
        )
    except PIDDoesNotExistError as e:
        add_cds_url(multipart_json)
        multipart_record = import_record(
            multipart_json,
            rectype="multipart",
            legacy_id=multipart_json["legacy_recid"],
        )
        series_indexer.index(multipart_record)
    volumes_items_list = json_record["_migration"]["items"]
    volumes_identifiers_list = json_record["_migration"]["volumes_identifiers"]
    volumes_urls_list = json_record["_migration"]["volumes_urls"]

    lists_lengths = [
        len(entry)
        for entry in [
            volumes_urls_list,
            volumes_items_list,
            volumes_identifiers_list,
        ]
    ]

    too_many_volumes = any(lists_lengths) > len(volume_list)

    if too_many_volumes:
        raise ManualImportRequired(
            "Record has more additional volume information "
            "entries than the number of indicated volumes"
        )

    for volume in volume_list:
        replace_fields_in_volume(document_json_template, volume, json_record)
        document_record = import_record(
            document_json_template,
            rectype="document",
            legacy_id=json_record["legacy_recid"],
            # we don't mint the legacy pid for these documents, since they
            # never were records on legacy, only it's parent multipart was
            mint_legacy_pid=False,
        )

        document_indexer.index(document_record)

        create_parent_child_relation(
            multipart_record,
            document_record,
            MULTIPART_MONOGRAPH_RELATION,
            volume.get("volume"),
        )
        db.session.commit()

        RecordRelationIndexer().index(document_record, multipart_record)
    return multipart_record


def import_multipart(json_record):
    """Import multipart record."""
    document_indexer = current_app_ils.document_indexer
    series_indexer = current_app_ils.series_indexer
    document_cls = current_app_ils.document_record_cls

    multipart_record = None
    multipart_id = json_record["_migration"].get("multipart_id")

    # volume specific information
    volumes = json_record["_migration"]["volumes"]

    if multipart_id:
        # try to check if the multipart already exists
        # (from previous dump file)
        multipart_record = get_multipart_by_multipart_id(multipart_id.upper())
    # series with record per volume shouldn't have more than one volume
    # in the list
    if len(volumes) != 1:
        raise ManualImportRequired("Matched volumes number incorrect.")

    # split json for multipart (series rectype) and
    # document (common data for all volumes, to be stored on document rectype)
    multipart_json = clean_document_json_for_multipart(
        json_record,
        include_keys=[
            "publication_year",
        ],
    )
    publisher = json_record.get("imprint", {}).get("publisher")
    if publisher:
        multipart_json["publisher"] = publisher

    document_json = exclude_multipart_fields(json_record)
    document_json["title"] = volumes[0]["title"]
    add_cds_url(document_json)

    # series with separate record per volume
    # (identified together with multipart id)
    if not multipart_record:
        multipart_record = import_record(
            multipart_json,
            rectype="multipart",
            legacy_id=json_record["legacy_recid"],
            # we don't mint the legacy pid for these series, since they
            # never were records on legacy, only it's volumes were
            mint_legacy_pid=False,
        )
    try:
        # check if the document already exists
        legacy_pid_type = current_app.config["CDS_ILS_RECORD_LEGACY_PID_TYPE"]
        document_record = get_record_by_legacy_recid(
            document_cls, legacy_pid_type, document_json["legacy_recid"]
        )
        # try to create relation (should fail if already exists)
        create_parent_child_relation(
            multipart_record,
            document_record,
            MULTIPART_MONOGRAPH_RELATION,
            volumes[0]["volume"],
        )
        db.session.commit()
        return multipart_record
    except PIDDoesNotExistError as e:
        document_record = import_record(
            document_json, rectype="document", legacy_id=document_json["legacy_recid"]
        )
        document_indexer.index(document_record)

        create_parent_child_relation(
            multipart_record,
            document_record,
            MULTIPART_MONOGRAPH_RELATION,
            volumes[0]["volume"],
        )
        db.session.commit()
        # the multipart needs to be indexed immediately,
        # because we search multipart_id to match next volumes
        series_indexer.index(multipart_record)

        RecordRelationIndexer().index(document_record, multipart_record)

        return multipart_record
