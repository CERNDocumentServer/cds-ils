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
from invenio_app_ils.errors import RecordRelationsError
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.records_relations.api import RecordRelationsParentChild, \
    RecordRelationsSiblings
from invenio_app_ils.relations.api import MULTIPART_MONOGRAPH_RELATION, \
    SERIAL_RELATION, Relation
from invenio_db import db

from cds_ils.literature.api import get_record_by_legacy_recid
from cds_ils.migrator.documents.api import \
    search_documents_with_siblings_relations
from cds_ils.migrator.errors import DocumentMigrationError, \
    MultipartMigrationError
from cds_ils.migrator.series.api import create_multipart_volumes, \
    get_migrated_volume_by_serial_title, get_multipart_by_legacy_recid, \
    get_serials_by_child_recid


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


def create_sibling_child_relation(first, second, relation_type):
    """Create parent child relations."""
    rr = RecordRelationsSiblings()
    click.echo(
        "Creating relations: {0} - {1}".format(first["pid"], second["pid"])
    )
    rr.add(
        first=first,
        second=second,
        relation_type=relation_type,
    )


def migrate_siblings_relation():
    """Create siblings relations."""
    document_class = current_app_ils.document_record_cls

    search = search_documents_with_siblings_relations()
    results = search.scan()
    for document in results:
        relations = document["_migration"]["related"]

        for relation in relations:
            related_sibling = None
            try:
                related_sibling = get_record_by_legacy_recid(
                    document_class, relation["related_recid"])
            except DocumentMigrationError as e:
                pass

            # try to find sibling in series
            if related_sibling is None:
                try:
                    related_sibling = get_multipart_by_legacy_recid(
                        relation["related_recid"])
                except MultipartMigrationError as e:
                    continue

            # validate relation type
            relation_type = Relation.get_relation_by_name(
                relation["relation_type"])

            # create relation
            if related_sibling:
                current_document_record = \
                    document_class.get_record_by_pid(document.pid)
                try:
                    create_sibling_child_relation(current_document_record,
                                                  related_sibling,
                                                  relation_type=relation_type)
                    db.session.commit()
                except RecordRelationsError as e:
                    click.secho(
                        e.description, fg="red"
                    )
                    continue


def link_and_create_multipart_volumes():
    """Link and create multipart volume records."""
    click.echo("Creating document volumes and multipart relations...")
    document_search = current_app_ils.document_search_cls()

    search = document_search.filter("term", _migration__is_multipart=True)
    for hit in search.scan():
        if "legacy_recid" not in hit:
            continue
        click.secho(
            "Linking multipart {}...".format(hit.legacy_recid), fg="green"
        )
        multipart = get_multipart_by_legacy_recid(hit.legacy_recid)
        documents = create_multipart_volumes(
            hit.pid, hit.legacy_recid, hit._migration.volumes
        )

        for document in documents:
            if document and multipart:
                click.echo(
                    "Creating relations: {0} - {1}".format(
                        multipart["pid"], document["pid"]
                    )
                )
                create_parent_child_relation(
                    multipart,
                    document,
                    MULTIPART_MONOGRAPH_RELATION,
                    document["volume"],
                )


def link_documents_and_serials():
    """Link documents/multiparts and serials."""
    document_class = current_app_ils.document_record_cls
    document_search = current_app_ils.document_search_cls()
    series_class = current_app_ils.series_record_class
    series_search = current_app_ils.series_search_cls()

    def link_records_and_serial(record_cls, search):
        for hit in search.scan():
            # Skip linking if the hit doesn't have a legacy recid since it
            # means it's a volume of a multipart
            if "legacy_recid" not in hit:
                continue
            record = record_cls.get_record_by_pid(hit.pid)
            for serial in get_serials_by_child_recid(hit.legacy_recid):
                volume = get_migrated_volume_by_serial_title(
                    record, serial["title"]
                )
                create_parent_child_relation(
                    serial, record, SERIAL_RELATION, volume
                )

    click.echo("Creating serial relations...")
    link_records_and_serial(
        document_class,
        document_search.filter("term", _migration__has_serial=True)
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
