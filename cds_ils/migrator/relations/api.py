# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator API."""
import logging

import click
from flask import current_app
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.records_relations.api import (
    RecordRelationsParentChild,
    RecordRelationsSequence,
    RecordRelationsSiblings,
)
from invenio_app_ils.records_relations.indexer import RecordRelationIndexer
from invenio_app_ils.relations.api import EDITION_RELATION, SERIAL_RELATION, Relation
from invenio_db import db
from invenio_search.engine import dsl

from cds_ils.literature.api import get_record_by_legacy_recid
from cds_ils.migrator.default_records import MIGRATION_DESIGN_PID
from cds_ils.migrator.errors import RelationMigrationError
from cds_ils.migrator.handlers import relation_exception_handlers
from cds_ils.migrator.series.api import (
    get_migrated_volume_by_serial_title,
    get_serials_by_child_recid,
)


def create_parent_child_relation(parent, child, relation_type, volume):
    """Create parent child relations."""
    relations_logger = logging.getLogger("relations_logger")

    rr = RecordRelationsParentChild()
    click.echo("Creating relations: {0} - {1}".format(parent["pid"], child["pid"]))
    rr.add(
        parent=parent,
        child=child,
        relation_type=relation_type,
        volume=str(volume) if volume else None,
    )

    relations_logger.info(
        "Created: {0} - {1}".format(parent["pid"], child["pid"]),
        extra=dict(legacy_id=None, status="SUCCESS", new_pid=parent["pid"]),
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
        create_parent_child_relation(serial, record, SERIAL_RELATION, volume=None)
        RecordRelationIndexer().index(record, serial)

    if design_report in record["_migration"]["serials"]:
        create_relation(MIGRATION_DESIGN_PID)


def create_sibling_relation(first, second, relation_type, **kwargs):
    """Create sibling relations."""
    relations_logger = logging.getLogger("relations_logger")

    rr = RecordRelationsSiblings()
    click.echo("Creating relations: {0} - {1}".format(first["pid"], second["pid"]))
    rr.add(
        first=first,
        second=second,
        relation_type=relation_type,
        **kwargs,
    )

    relations_logger.info(
        "Created: {0} - {1}".format(first["pid"], second["pid"]),
        extra=dict(legacy_id=None, status="SUCCESS", new_pid=first["pid"]),
    )


def create_sequence_relation(previous_rec, next_rec, relation_type):
    """Create sequence relations."""
    relations_logger = logging.getLogger("relations_logger")
    rr = RecordRelationsSequence()
    click.echo(
        "Creating relations: {0} - {1}".format(previous_rec["pid"], next_rec["pid"])
    )
    rel = Relation(relation_type)
    if not rel.relation_exists(previous_rec.pid, next_rec.pid):
        rr.add(
            previous_rec=previous_rec,
            next_rec=next_rec,
            relation_type=relation_type,
        )
        relations_logger.info(
            "Created: {0} - {1}".format(previous_rec["pid"], next_rec["pid"]),
            extra=dict(legacy_id=None, status="SUCCESS", new_pid=previous_rec["pid"]),
        )


def validate_edition_field(current_document_record, related_sibling, relation):
    """Validate edition field for relation."""
    edition = current_document_record.get("edition")
    related_edition = related_sibling.get("edition")

    if edition and related_edition:
        return

    if not edition:
        relations_related_sibling = related_sibling["_migration"]["related"]
        symmetrical_relation = next(
            (
                x
                for x in relations_related_sibling
                if x["relation_type"] == EDITION_RELATION.name
                and x["related_recid"] == current_document_record["legacy_recid"]
            ),
            None,
        )

        if not symmetrical_relation:
            raise RelationMigrationError("Edition information missing.")
        current_document_record["edition"] = symmetrical_relation[
            "relation_description"
        ].replace("ed.", "")
        current_document_record.commit()
        db.session.commit()

    if not related_edition:
        related_sibling["edition"] = relation["relation_description"].replace("ed.", "")
        related_sibling.commit()
        db.session.commit()


def link_documents_and_serials():
    """Link documents/multiparts and serials."""
    document_class = current_app_ils.document_record_cls
    document_search = current_app_ils.document_search_cls()
    series_class = current_app_ils.series_record_cls
    series_search = current_app_ils.series_search_cls()
    journal_legacy_pid_type = current_app.config["CDS_ILS_SERIES_LEGACY_PID_TYPE"]

    def link_records_and_serial(record_cls, search):
        click.echo(f"FOUND {search.count()} serial related records.")
        for hit in search.params(scroll="1h").scan():
            try:
                click.echo(f"Processing record {hit.pid}.")
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
                # mark done
                record["_migration"]["has_serial"] = False
                record.commit()
                db.session.commit()
            except Exception as exc:
                handler = relation_exception_handlers.get(exc.__class__)
                if handler:
                    legacy_recid = None
                    if hasattr(hit, "legacy_recid"):
                        legacy_recid = hit.legacy_recid
                    handler(exc, new_pid=hit.pid, legacy_id=legacy_recid)
                else:
                    raise exc

    def link_record_and_journal(record_cls, search):
        click.echo(f"FOUND {search.count()} journal related records.")
        for hit in search.params(scroll="1h").scan():
            click.echo(f"Processing record {hit.pid}.")
            try:
                if "legacy_recid" not in hit:
                    continue
                record = record_cls.get_record_by_pid(hit.pid)
                for journal in hit["_migration"]["journal_record_legacy_recids"]:
                    serial = get_record_by_legacy_recid(
                        series_class, journal_legacy_pid_type, journal["recid"]
                    )
                    create_parent_child_relation(
                        serial, record, SERIAL_RELATION, journal["volume"]
                    )

                    # mark done
                    record["_migration"]["has_journal"] = False
                    record.commit()
                    db.session.commit()
            except Exception as exc:
                handler = relation_exception_handlers.get(exc.__class__)
                if handler:
                    legacy_recid = None
                    if hasattr(hit, "legacy_recid"):
                        legacy_recid = hit.legacy_recid
                    handler(exc, new_pid=hit.pid, legacy_id=legacy_recid)
                else:
                    raise exc

    click.echo("Creating serial relations...")

    link_records_and_serial(
        document_class, document_search.filter("term", _migration__has_serial=True)
    )
    link_records_and_serial(
        series_class,
        series_search.filter(
            "bool",
            filter=[
                dsl.Q("term", mode_of_issuance="MULTIPART_MONOGRAPH"),
                dsl.Q("term", _migration__has_serial=True),
            ],
        ),
    )
    link_record_and_journal(
        document_class,
        document_search.filter("term", _migration__has_journal=True),
    )
