# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer module."""
from invenio_app_ils.proxies import current_app_ils
from invenio_search.engine import dsl


def search_documents_by_isbn(isbn):
    """Find document by ISBN."""
    document_search = current_app_ils.document_search_cls()
    search = document_search.query(
        "bool",
        must=[
            dsl.Q("term", identifiers__scheme="ISBN"),
            dsl.Q("term", identifiers__value=isbn),
        ],
    )
    return search


def search_documents_by_doi(doi):
    """Find document by ISBN."""
    document_search = current_app_ils.document_search_cls()
    search = document_search.query(
        "bool",
        must=[
            dsl.Q("term", identifiers__scheme="DOI"),
            dsl.Q("term", identifiers__value=doi),
        ],
    )
    return search


def search_document_by_title_authors(title, authors, subtitle=None):
    """Find document by title and authors."""
    document_search = current_app_ils.document_search_cls()

    title = " ".join(
        title.lower().split()
    ).strip()  # Normalized title search for documents
    if subtitle:
        search = (
            document_search.filter("term", title__normalized_keyword=title)
            .filter("match", alternative_titles__value=subtitle)
            .filter("match", authors__full_name__full_words=" ".join(authors))
        )
    else:
        search = document_search.filter("term", title__normalized_keyword=title).filter(
            "match", authors__full_name__full_words=" ".join(authors)
        )
    return search


def fuzzy_search_document(title, authors):
    """Search fuzzy matches of document and title."""
    # check the fuzzy search options under:
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-fuzzy-query.html
    document_search = current_app_ils.document_search_cls()
    search = document_search.query(
        dsl.query.Match(
            title__keyword={
                "fuzziness": "AUTO",
                "fuzzy_transpositions": "true",
                "query": title,
            }
        )
    ).filter(
        dsl.query.Match(
            authors__full_name={
                "query": " ".join(authors),
                "fuzziness": "AUTO",
                "fuzzy_transpositions": "true",
            }
        )
    )
    return search
