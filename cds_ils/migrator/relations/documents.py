# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator API."""

import click
from flask import current_app
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.relations.api import (
    EDITION_RELATION,
    OTHER_RELATION,
    ParentChildRelation,
    Relation,
)
from invenio_db import db
from invenio_pidstore.errors import PIDDoesNotExistError

from cds_ils.literature.api import get_record_by_legacy_recid
from cds_ils.migrator.documents.api import search_documents_with_siblings_relations
from cds_ils.migrator.errors import RelationMigrationError
from cds_ils.migrator.handlers import relation_exception_handlers
from cds_ils.migrator.relations.api import (
    create_sibling_relation,
    validate_edition_field,
)


def find_related_record(relation):
    """Find related document record or first volume of series."""
    document_class = current_app_ils.document_record_cls
    series_class = current_app_ils.series_record_cls
    document_legacy_pid_type = current_app.config["CDS_ILS_RECORD_LEGACY_PID_TYPE"]
    try:
        related_sibling = get_record_by_legacy_recid(
            document_class,
            document_legacy_pid_type,
            relation["related_recid"],
        )
        return related_sibling
    except PIDDoesNotExistError as e:
        # If there is no document it means it can be related to a
        # multipart. If this is the case we relate it to the first
        # document of the multipart
        series_legacy_pid = current_app.config["CDS_ILS_SERIES_LEGACY_PID_TYPE"]
        try:
            # Search for the series with related legacy_recid from
            # the document
            related_series = get_record_by_legacy_recid(
                series_class,
                series_legacy_pid,
                relation["related_recid"],
            )
            multipart_relation = Relation.get_relation_by_name("multipart_monograph")
            pcr = ParentChildRelation(multipart_relation)
            volumes = pcr.get_children_of(related_series.pid)

            if len(volumes) > 0:
                # Selects the first volume as the one to be related
                # with the document
                related_sibling = document_class.get_record_by_pid(volumes[0].pid_value)
                return related_sibling
            else:
                click.secho(
                    "No document related volume found with legacy_recid: {}".format(
                        relation["related_recid"]
                    ),
                    fg="red",
                )
                raise RelationMigrationError(
                    f"No related volume record found "
                    f"with legacy_recid {relation['related_recid']}"
                )
        except PIDDoesNotExistError as e:
            click.secho(
                "No record found with legacy_recid: {}".format(
                    relation["related_recid"]
                ),
                fg="red",
            )
            raise RelationMigrationError(
                f"No related record found "
                f"with legacy_recid {relation['related_recid']}"
            )


def migrate_document_siblings_relation(raise_exceptions=False):
    """Create siblings relations."""
    document_class = current_app_ils.document_record_cls

    search = search_documents_with_siblings_relations()
    results = search.params(scroll="4h").scan()

    for document in results:
        current_document_record = document_class.get_record_by_pid(document.pid)
        relations = current_document_record["_migration"]["related"]
        for relation in relations:
            try:
                # clean the found sibling
                related_sibling = None
                extra_metadata = {}
                related_sibling = find_related_record(relation)
                if not related_sibling:
                    continue

                # validate relation type
                relation_type = Relation.get_relation_by_name(relation["relation_type"])

                if relation_type.name == EDITION_RELATION.name:
                    validate_edition_field(
                        current_document_record, related_sibling, relation
                    )

                if relation_type.name == OTHER_RELATION.name:
                    extra_metadata.update({"note": relation["relation_description"]})
                # create relation
                if related_sibling and related_sibling["pid"] != document.pid:
                    create_sibling_relation(
                        current_document_record,
                        related_sibling,
                        relation_type,
                        **extra_metadata,
                    )
                    db.session.commit()
            except Exception as exc:
                click.secho(str(exc), fg="red")
                handler = relation_exception_handlers.get(exc.__class__)
                if handler:
                    handler(
                        exc,
                        new_pid=current_document_record["pid"],
                        legacy_id=current_document_record.get("legacy_recid"),
                    )
                else:
                    if raise_exceptions:
                        raise exc
        current_document_record["_migration"]["has_related"] = False
        current_document_record.commit()
        db.session.commit()
