# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS document migrator API."""

import click
from invenio_app_ils.proxies import current_app_ils
from invenio_search.engine import dsl

from cds_ils.migrator.errors import DocumentMigrationError


def get_document_by_barcode(barcode):
    """Return document from barcode search."""
    document_class = current_app_ils.document_record_cls
    document_search = current_app_ils.document_search_cls()
    search = document_search.query(
        "query_string", query='_migration.items.barcode:"{}"'.format(barcode)
    )

    result = search.execute()
    hits_total = result.hits.total.value

    if hits_total == 1:
        click.secho(
            "! document found with item barcode {}".format(barcode),
            fg="green",
        )
        return document_class.get_record_by_pid(result.hits[0].pid)

    else:
        click.secho(
            "no document found with barcode {}".format(barcode),
            fg="red",
        )
        raise DocumentMigrationError(
            "no document found with barcode {}".format(barcode)
        )


def get_all_documents_with_files():
    """Return all documents with files to be migrated."""
    document_search = current_app_ils.document_search_cls()
    search = document_search.filter(
        "bool",
        filter=[
            dsl.Q("term", _migration__has_files=True),
        ],
    )
    return search


def get_documents_with_proxy_eitems():
    """Return documents with eitems behind proxy to be migrated."""
    document_search = current_app_ils.document_search_cls()
    search = document_search.filter(
        "bool",
        filter=[
            dsl.Q("term", _migration__eitems_has_proxy=True),
        ],
    )
    return search


def get_documents_with_ebl_eitems():
    """Return documents with eitems from EBL provider to be migrated."""
    document_search = current_app_ils.document_search_cls()
    search = document_search.filter(
        "bool",
        filter=[
            dsl.Q("term", _migration__eitems_has_ebl=True),
        ],
    )
    return search


def get_documents_with_safari_eitems():
    """Return documents with eitems from Safari provider to be migrated."""
    document_search = current_app_ils.document_search_cls()
    search = document_search.filter(
        "bool",
        filter=[
            dsl.Q("term", _migration__eitems_has_safari=True),
        ],
    )
    return search


def get_documents_with_external_eitems():
    """Return documents with eitems from external providers to be migrated."""
    document_search = current_app_ils.document_search_cls()
    search = document_search.filter(
        "bool",
        filter=[
            dsl.Q("term", _migration__eitems_has_external=True),
        ],
    )
    return search


def search_documents_with_siblings_relations():
    """Return documents with siblings relations."""
    document_search = current_app_ils.document_search_cls()
    search = document_search.filter(
        "bool",
        filter=[
            dsl.Q("term", _migration__has_related=True),
        ],
    )
    return search
