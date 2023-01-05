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
    SEQUENCE_RELATION_TYPES,
    SIBLINGS_RELATION_TYPES,
    Relation,
)
from invenio_db import db
from invenio_pidstore.errors import PIDDoesNotExistError

from cds_ils.literature.api import get_record_by_legacy_recid
from cds_ils.migrator.errors import RelationMigrationError
from cds_ils.migrator.handlers import relation_exception_handlers
from cds_ils.migrator.relations.api import (
    create_sequence_relation,
    create_sibling_relation,
)
from cds_ils.migrator.series.api import search_series_with_relations


def find_related_record(relation, series):
    """Find the correct related record."""
    series_class = current_app_ils.series_record_cls
    document_class = current_app_ils.document_record_cls
    series_legacy_pid_type = current_app.config["CDS_ILS_SERIES_LEGACY_PID_TYPE"]
    document_legacy_pid_type = current_app.config["CDS_ILS_RECORD_LEGACY_PID_TYPE"]
    try:
        related_series = get_record_by_legacy_recid(
            series_class, series_legacy_pid_type, relation["related_recid"]
        )
        return related_series
    except PIDDoesNotExistError as e:
        related_doc = get_record_by_legacy_recid(
            document_class, document_legacy_pid_type, relation["related_recid"]
        )
        if related_doc:
            # should be handled from the document side
            # so remove (no series-document relations allowed)
            series["_migration"]["related"].remove(relation)
            return
        else:
            raise RelationMigrationError(
                f"{series['pid']}: Related series with "
                f"legacy recid {relation['related_recid']} not found"
            )


def migrate_series_relations(raise_exceptions=False):
    """Create relations for series."""
    series_class = current_app_ils.series_record_cls
    search = search_series_with_relations()
    results = search.params(scroll="4h").scan()

    for series in results:
        current_series_record = series_class.get_record_by_pid(series.pid)
        relations = current_series_record["_migration"]["related"]

        for relation in relations:
            try:
                # clean the found sibling
                related_series = None
                related_series = find_related_record(relation, series)
                if not related_series:
                    continue

                # validate relation type
                relation_type = Relation.get_relation_by_name(relation["relation_type"])
                # create relation
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
            except Exception as exc:
                click.secho(str(exc), fg="red")
                handler = relation_exception_handlers.get(exc.__class__)
                if handler:
                    handler(
                        exc,
                        new_pid=series["pid"],
                        legacy_id=current_series_record.get("legacy_recid"),
                    )
                else:
                    raise exc
        current_series_record["_migration"]["has_related"] = False
        current_series_record.commit()
        db.session.commit()
