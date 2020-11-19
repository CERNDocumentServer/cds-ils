# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer documents module."""
import uuid
from copy import deepcopy

import click
from invenio_app_ils.documents.api import DocumentIdProvider
from invenio_app_ils.errors import IlsValidationError
from invenio_app_ils.proxies import current_app_ils
from invenio_db import db

from cds_ils.importer.documents.api import fuzzy_search_document, \
    search_document_by_title_authors, search_documents_by_doi, \
    search_documents_by_isbn


class DocumentImporter(object):
    """Document importer class."""

    def __init__(
        self,
        json_metadata,
        helper_metadata_fields,
        metadata_provider,
        update_document_fields,
    ):
        """Constructor."""
        self.helper_metadata_fields = helper_metadata_fields
        self.json_data = json_metadata
        self.metadata_provider = metadata_provider
        self.update_document_fields = update_document_fields

    def _set_record_import_source(self, record_dict):
        """Set the import source for document."""
        record_dict["created_by"] = {
            "type": "import",
            "value": self.metadata_provider,
        }

    def _before_create(self):
        """Perform before create metadata modification."""
        cleaned = deepcopy(self.json_data)
        for field in self.helper_metadata_fields:
            if field in cleaned:
                del cleaned[field]
        # save the import source
        self._set_record_import_source(cleaned)
        return cleaned

    def create_document(self):
        """Create a new record from dump."""
        cleaned_json = self._before_create()
        document_class = current_app_ils.document_record_cls
        # Reserve record identifier, create record and recid pid in one
        # operation.
        record_uuid = uuid.uuid4()
        try:
            with db.session.begin_nested():
                provider = DocumentIdProvider.create(
                    object_type="rec",
                    object_uuid=record_uuid,
                )
                cleaned_json["pid"] = provider.pid.pid_value
                document = document_class.create(cleaned_json, record_uuid)
            db.session.commit()
            return document
        except IlsValidationError as e:
            click.secho("Field: {}".format(e.errors[0].res["field"]), fg="red")
            click.secho(e.original_exception.message, fg="red")
            db.session.rollback()
            # raise e TODO handle the incorrect records in the logging

    def _update_field_identifiers(self, matched_document):
        """Update isbns of a given document."""
        existing_identifiers = matched_document["identifiers"]
        new_identifiers = [
            elem
            for elem in self.json_data["identifiers"]
            if elem not in existing_identifiers
        ]

        return existing_identifiers + new_identifiers

    def update_document(self, matched_document):
        """Update document record."""
        for field in self.update_document_fields:
            update_field_method = getattr(
                self, "_update_field_{}".format(field), None
            )
            if update_field_method:
                matched_document[field] = update_field_method(matched_document)
            else:
                matched_document[field] = self.json_data[field]

        try:
            matched_document.commit()
            db.session.commit()
        except IlsValidationError as e:
            click.secho("Field: {}".format(e.errors[0].res["field"]), fg="red")
            click.secho(e.original_exception.message, fg="red")
            db.session.rollback()

    def search_for_matching_documents(self):
        """Find matching documents."""
        isbn_list = [
            identifier["value"]
            for identifier in self.json_data.get("identifiers", [])
            if identifier["scheme"] == "ISBN"
        ]

        doi_list = [
            identifier["value"]
            for identifier in self.json_data.get("identifiers", [])
            if identifier["scheme"] == "DOI"
        ]

        matches = []

        # check by isbn first
        for isbn in isbn_list:
            search = search_documents_by_isbn(isbn)
            results = search.scan()
            matches += [x.pid for x in results if x.pid not in matches]

        # check by doi

        for doi in doi_list:
            search = search_documents_by_doi(doi)
            results = search.scan()
            matches += [x.pid for x in results if x.pid not in matches]

        is_part_of_serial = self.json_data.get("_serial", None)
        title = self.json_data.get("title", None)

        if not is_part_of_serial and title:
            # check by title and authors, exact matching
            authors = [
                author["full_name"]
                for author in self.json_data.get("authors", [])
            ]
            subtitle = None
            subtitle_obj = [
                alt_title
                for alt_title in self.json_data.get("alternative_titles", [])
                if alt_title["type"] == "SUBTITLE"
            ]
            if subtitle_obj:
                subtitle = subtitle_obj[0]["value"]

            search = search_document_by_title_authors(
                title, authors, subtitle=subtitle
            )
            results = search.scan()
            matches += [x.pid for x in results if x.pid not in matches]

        return matches

    def fuzzy_match_documents(self):
        """Fuzzy search documents."""
        is_part_of_serial = self.json_data.get("_serial", None)
        title = self.json_data.get("title", None)

        if is_part_of_serial or not title:
            return []
        authors = [
            author["full_name"] for author in self.json_data.get("authors", [])
        ]

        fuzzy_results = fuzzy_search_document(title, authors).scan()

        return fuzzy_results
