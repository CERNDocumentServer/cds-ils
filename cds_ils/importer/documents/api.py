# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer module."""
import click
from elasticsearch_dsl import Q
from elasticsearch_dsl.query import Match
from invenio_app_ils.proxies import current_app_ils

from cds_ils.importer.errors import DocumentImportError


def check_search_results(
    result,
    search_term,
    search_term_name,
    raise_on_empty=False,
    raise_on_many=True,
):
    """Check number of search results."""
    hits_total = result.hits.total.value

    if hits_total == 0:

        click.secho(
            "no document found with {}:{}".format(
                search_term_name, search_term
            ),
            fg="red",
        )
        if raise_on_empty:
            raise DocumentImportError(
                "no document found with {} {}".format(
                    search_term_name, search_term
                )
            )
    elif hits_total > 1:
        click.secho(
            "found more than one document with {} {}".format(
                search_term_name, search_term
            ),
            fg="red",
        )
        if raise_on_many:
            raise DocumentImportError(
                "found more than one document with {} {}".format(
                    search_term_name, search_term
                )
            )
    return hits_total


def search_documents_by_isbn(isbn):
    """Find document by ISBN."""
    document_search = current_app_ils.document_search_cls()
    search = document_search.query(
        "bool",
        must=[
            Q("term", identifiers__scheme="ISBN"),
            Q("term", identifiers__value=isbn),
        ],
    )
    return search


def search_documents_by_doi(doi):
    """Find document by ISBN."""
    document_search = current_app_ils.document_search_cls()
    search = document_search.query(
        "bool",
        must=[
            Q("term", identifiers__scheme="DOI"),
            Q("term", identifiers__value=doi),
        ],
    )
    return search


def search_document_by_title_authors(title, authors, subtitle=None):
    """Find document by title and authors."""
    document_search = current_app_ils.document_search_cls()
    if subtitle:
        search = (
            document_search.query("match", title=title)
            .filter("match", alternative_titles__value=subtitle)
            .filter("match", authors__full_name=" ".join(authors))
        )
    else:
        search = document_search.query("match", title=title).filter(
            "match", authors__full_name=" ".join(authors)
        )

    return search


def fuzzy_search_document(title, authors):
    """Search fuzzy matches of document and title."""
    # check the fuzzy search options under:
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-fuzzy-query.html
    document_search = current_app_ils.document_search_cls()
    search = document_search.query(
        Match(
            title={
                "fuzziness": "AUTO",
                "fuzzy_transpositions": "true",
                "query": title,
            }
        )
    ).filter(
        Match(
            authors__full_name={
                "query": "".join(authors),
                "fuzziness": "AUTO",
                "fuzzy_transpositions": "true",
            }
        )
    )
    return search


def get_document_by_legacy_recid(legacy_recid):
    """Search documents by its legacy recid."""
    document_search = current_app_ils.document_search_cls()
    document_cls = current_app_ils.document_record_cls

    search = document_search.query(
        "bool", filter=[Q("term", legacy_recid=legacy_recid)]
    )
    result = search.execute()
    hits_total = check_search_results(result, legacy_recid, "legacy recid")

    if hits_total == 1:
        return document_cls.get_record_by_pid(result.hits[0].pid)
