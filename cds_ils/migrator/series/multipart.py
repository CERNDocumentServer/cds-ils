# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator."""

import logging

from invenio_app_ils.relations.api import MULTIPART_MONOGRAPH_RELATION
from invenio_pidstore.errors import PIDDoesNotExistError

from cds_ils.importer.errors import ManualImportRequired
from cds_ils.literature.api import get_record_by_legacy_recid
from cds_ils.migrator.api import import_record
from cds_ils.migrator.errors import MultipartMigrationError
from cds_ils.migrator.relations.api import create_parent_child_relation
from cds_ils.migrator.series.api import clean_document_json_for_multipart, \
    exclude_multipart_fields, get_multipart_by_multipart_id, \
    replace_fields_in_volume
from cds_ils.migrator.utils import model_provider_by_rectype

migrated_logger = logging.getLogger("migrated_records")
records_logger = logging.getLogger("records_errored")


def import_multivolume(json_record):
    """Import multivolume type of multipart."""
    legacy_recid = json_record["legacy_recid"]
    series_cls, series_pid_provider = model_provider_by_rectype("multipart")
    document_cls, document_pid_provider = model_provider_by_rectype("document")

    # build multipart dict - leave the legacy_recid attached
    multipart_json = clean_document_json_for_multipart(
        json_record, include_keys=["legacy_recid"]
    )

    # prepare json for each volume
    document_json_template = exclude_multipart_fields(
        json_record, exclude_keys=["legacy_recid"]
    )

    volume_list = json_record["_migration"]["volumes"]

    try:
        get_record_by_legacy_recid(series_cls, legacy_recid)
        raise MultipartMigrationError(
            f"Multipart {legacy_recid} was already " f"processed. Aborting."
        )
    except PIDDoesNotExistError as e:
        multipart_record = import_record(
            multipart_json,
            series_cls,
            series_pid_provider,
            legacy_id_key="title",
        )
    volumes_items_list = json_record["_migration"]["items"]
    volumes_identifiers_list = json_record["_migration"]["volumes_identifiers"]
    volumes_urls_list = json_record["_migration"]["volumes_urls"]

    lists_lenghts = [
        len(entry)
        for entry in [
            volumes_urls_list,
            volumes_items_list,
            volumes_identifiers_list,
        ]
    ]

    too_many_volumes = any(lists_lenghts) > len(volume_list)

    if too_many_volumes:
        raise ManualImportRequired(
            "Record has more additional volume information "
            "entries than the number of indicated volumes"
        )

    for volume in volume_list:
        replace_fields_in_volume(document_json_template, volume, json_record)
        document_record = import_record(
            document_json_template,
            document_cls,
            document_pid_provider,
            legacy_id_key="title",
        )
        create_parent_child_relation(
            multipart_record,
            document_record,
            MULTIPART_MONOGRAPH_RELATION,
            volume.get("volume"),
        )
    return multipart_record


def import_multipart(json_record):
    """Import multipart record."""
    multipart_record = None
    multipart_id = json_record["_migration"].get("multipart_id")
    series_cls, series_pid_provider = model_provider_by_rectype("multipart")
    document_cls, document_pid_provider = model_provider_by_rectype("document")

    multipart_json = clean_document_json_for_multipart(json_record)
    document_json = exclude_multipart_fields(json_record)
    volumes = json_record["_migration"]["volumes"]

    if multipart_id:
        # try to check if the multipart already exists
        multipart_record = get_multipart_by_multipart_id(multipart_id)
    # series with record per volume shouldn't have more than one volume
    # in the list
    if len(volumes) != 1:
        raise ManualImportRequired("Matched volumes number incorrect.")

    # series with separate record per volume
    # (identified together with multipart id)
    if not multipart_record:
        multipart_record = import_record(
            multipart_json,
            series_cls,
            series_pid_provider,
            legacy_id_key="title",
        )
    try:
        # check if the document already exists
        document_record = get_record_by_legacy_recid(
            document_cls, document_json["legacy_recid"]
        )
        # try to create relation (should fail if already exists)
        create_parent_child_relation(
            multipart_record,
            document_record,
            MULTIPART_MONOGRAPH_RELATION,
            volumes[0]["volume"],
        )
        return multipart_record
    except PIDDoesNotExistError as e:
        document_record = import_record(
            document_json, document_cls, document_pid_provider
        )
        create_parent_child_relation(
            multipart_record,
            document_record,
            MULTIPART_MONOGRAPH_RELATION,
            volumes[0]["volume"],
        )
        return multipart_record
