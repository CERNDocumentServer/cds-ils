# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator API."""

import click
from elasticsearch_dsl import Q
from flask import current_app
from invenio_app_ils.errors import RecordRelationsError
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.records_relations.api import RecordRelationsParentChild, \
    RecordRelationsSequence, RecordRelationsSiblings
from invenio_app_ils.records_relations.indexer import RecordRelationIndexer
from invenio_app_ils.relations.api import OTHER_RELATION, \
    SEQUENCE_RELATION_TYPES, SERIAL_RELATION, SIBLINGS_RELATION_TYPES, \
    Relation
from invenio_db import db
from invenio_pidstore.errors import PIDDoesNotExistError

from cds_ils.literature.api import get_record_by_legacy_recid
from cds_ils.migrator.default_records import MIGRATION_DESIGN_PID
from cds_ils.migrator.documents.api import \
    search_documents_with_siblings_relations
from cds_ils.migrator.series.api import get_migrated_volume_by_serial_title, \
    get_serials_by_child_recid, search_series_with_relations


def create_parent_child_relation(parent, child, relation_type, volume):
    """Create parent child relations."""
    rr = RecordRelationsParentChild()
    click.echo(
        "Creating relations: {0} - {1}".format(parent["pid"], child["pid"])
    )
    rr.add(
        parent=parent,
        child=child,
        relation_type=relation_type,
        volume=str(volume) if volume else None,
    )


def check_for_special_series(record):
    """Link documents and serials (DESIGN REPORT)."""
    series_class = current_app_ils.series_record_cls
    design_report = {
        "title": "DESIGN REPORT",
        "volume": None,
        "issn": None,
    }

    def create_relation(pid):
        serial = series_class.get_record_by_pid(pid)
        create_parent_child_relation(
            serial, record, SERIAL_RELATION, volume=None
        )
        RecordRelationIndexer().index(record, serial)

    if design_report in record["_migration"]["serials"]:
        create_relation(MIGRATION_DESIGN_PID)


def create_sibling_relation(first, second, relation_type, **kwargs):
    """Create sibling relations."""
    rr = RecordRelationsSiblings()
    click.echo(
        "Creating relations: {0} - {1}".format(first["pid"], second["pid"])
    )
    rr.add(
        first=first,
        second=second,
        relation_type=relation_type,
        **kwargs,
    )


def create_sequence_relation(previous_rec, next_rec, relation_type):
    """Create sequence relations."""
    rr = RecordRelationsSequence()
    click.echo(
        "Creating relations: {0} - {1}".format(
            previous_rec["pid"], next_rec["pid"]
        )
    )
    rel = Relation(relation_type)
    if not rel.relation_exists(previous_rec.pid, next_rec.pid):
        rr.add(
            previous_rec=previous_rec,
            next_rec=next_rec,
            relation_type=relation_type,
        )


def migrate_document_siblings_relation():
    """Create siblings relations."""
    document_class = current_app_ils.document_record_cls
    series_class = current_app_ils.series_record_cls

    search = search_documents_with_siblings_relations()
    results = search.scan()
    legacy_pid_type = current_app.config["CDS_ILS_RECORD_LEGACY_PID_TYPE"]

    extra_metadata = {}
    for document in results:
        relations = document["_migration"]["related"]

        for relation in relations:
            related_sibling = None
            try:
                related_sibling = get_record_by_legacy_recid(
                    document_class, legacy_pid_type, relation["related_recid"]
                )
            except PIDDoesNotExistError as e:
                pass

            # try to find sibling in series
            if related_sibling is None:
                try:
                    related_sibling = get_record_by_legacy_recid(
                        series_class,
                        legacy_pid_type,
                        relation["related_recid"],
                    )
                except PIDDoesNotExistError as e:
                    continue

            # validate relation type
            relation_type = Relation.get_relation_by_name(
                relation["relation_type"]
            )

            if relation_type == OTHER_RELATION.name:
                extra_metadata.update(
                    {"note": relation["relation_description"]}
                )
            # create relation
            if related_sibling and related_sibling["pid"] != document.pid:
                current_document_record = document_class.get_record_by_pid(
                    document.pid
                )

                try:
                    create_sibling_relation(
                        current_document_record,
                        related_sibling,
                        relation_type,
                        **extra_metadata,
                    )
                    db.session.commit()
                except RecordRelationsError as e:
                    click.secho(e.description, fg="red")
                    continue


def migrate_series_relations():
    """Create relations for series."""
    series_class = current_app_ils.series_record_cls
    search = search_series_with_relations()
    results = search.scan()
    legacy_pid_type = current_app.config["CDS_ILS_SERIES_LEGACY_PID_TYPE"]

    for series in results:
        relations = series["_migration"]["related"]

        for relation in relations:
            related_series = get_record_by_legacy_recid(
                series_class, legacy_pid_type, relation["related_recid"]
            )

            # validate relation type
            relation_type = Relation.get_relation_by_name(
                relation["relation_type"]
            )

            # create relation
            current_series_record = series_class.get_record_by_pid(series.pid)
            try:
                if relation_type in SIBLINGS_RELATION_TYPES:
                    create_sibling_relation(
                        current_series_record,
                        related_series,
                        relation_type,
                        note=relation["relation_description"],
                    )

                elif relation_type in SEQUENCE_RELATION_TYPES:
                    if relation["sequence_order"] == "previous":
                        create_sequence_relation(
                            current_series_record,
                            related_series,
                            relation_type,
                        )
                    else:
                        create_sequence_relation(
                            related_series,
                            current_series_record,
                            relation_type,
                        )
                db.session.commit()
            except RecordRelationsError as e:
                click.secho(e.description, fg="red")
                continue


def link_documents_and_serials():
    """Link documents/multiparts and serials."""
    document_class = current_app_ils.document_record_cls
    document_search = current_app_ils.document_search_cls()
    series_class = current_app_ils.series_record_cls
    series_search = current_app_ils.series_search_cls()
    legacy_pid_type = current_app.config["CDS_ILS_RECORD_LEGACY_PID_TYPE"]

    def link_records_and_serial(record_cls, search):
        for hit in search.scan():
            # Skip linking if the hit doesn't have a legacy recid since it
            # means it's a volume of a multipart
            if "legacy_recid" not in hit:
                continue
            record = record_cls.get_record_by_pid(hit.pid)
            check_for_special_series(record)
            for serial in get_serials_by_child_recid(hit.legacy_recid):
                volume = get_migrated_volume_by_serial_title(
                    record, serial["title"]
                )
                create_parent_child_relation(
                    serial, record, SERIAL_RELATION, volume
                )
                RecordRelationIndexer().index(record, serial)

    def link_record_and_journal(record_cls, search):
        for hit in search.scan():
            if "legacy_recid" not in hit:
                continue
            record = record_cls.get_record_by_pid(hit.pid)
            for journal in hit["_migration"]["journal_record_legacy_recids"]:
                serial = get_record_by_legacy_recid(
                    series_class, legacy_pid_type, journal["recid"]
                )
                create_parent_child_relation(
                    serial, record, SERIAL_RELATION, journal["volume"]
                )

                del record["publication_info"]
                record.commit()
                db.session.commit()

    click.echo("Creating serial relations...")
    link_records_and_serial(
        document_class,
        document_search.filter("term", _migration__has_serial=True),
    )
    link_records_and_serial(
        series_class,
        series_search.filter(
            "bool",
            filter=[
                Q("term", mode_of_issuance="MULTIPART_MONOGRAPH"),
                Q("term", _migration__has_serial=True),
            ],
        ),
    )
    link_record_and_journal(
        document_class,
        document_search.filter("term", _migration__has_journal=True),
    )
