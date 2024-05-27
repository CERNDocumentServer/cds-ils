# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer documents module."""
import datetime
import uuid
from copy import deepcopy

import click
from dateutil import parser
from invenio_app_ils.documents.api import DocumentIdProvider
from invenio_app_ils.errors import IlsValidationError
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.vocabularies.api import VOCABULARY_TYPE_LICENSE
from invenio_db import db
from invenio_jsonschemas import current_jsonschemas
from invenio_search.engine import search

from cds_ils.importer.documents.api import (
    fuzzy_search_document,
    search_document_by_title_authors,
    search_documents_by_doi,
    search_documents_by_isbn,
)
from cds_ils.importer.errors import SimilarityMatchUnavailable
from cds_ils.importer.vocabularies_validator import validator as vocabulary_validator

VOCABULARIES_FIELDS = {
    "alternative_identifiers": {
        "scheme": {
            "source": "json",
            "type": "alternative_identifier_scheme",
        },
    },
    "alternative_titles": {
        "type": {
            "source": "json",
            "type": "alternative_title_type",
        },
    },
    "authors": {
        "affiliations": {
            "identifiers": {
                "scheme": {
                    "source": "json",
                    "type": "affiliation_identifier_scheme",
                },
            }
        },
        "identifiers": {
            "scheme": {
                "source": "json",
                "type": "author_identifier_scheme",
            },
        },
        "roles": {
            "source": "json",
            "type": "author_role",
        },
        "type": {
            "source": "json",
            "type": "author_type",
        },
    },
    "identifiers": {
        "scheme": {
            "source": "json",
            "type": "identifier_scheme",
        },
        "material": {
            "source": "json",
            "type": "doc_identifiers_materials",
        },
    },
    "extensions": {
        "standard_review_applicability": {
            "source": "json",
            "type": "document_standard_reviews",
        },
        "unit_institution": {
            "source": "json",
            "type": "document_institutions",
        },
    },
    "conference_info": {
        "identifiers": {
            "scheme": {
                "source": "json",
                "type": "conference_identifier_scheme",
            }
        }
    },
    "licenses": {
        "license": {
            "source": "elasticsearch",
            "type": VOCABULARY_TYPE_LICENSE,
        },
    },
    "subjects": {
        "scheme": {
            "source": "json",
            "type": "doc_subjects",
        },
    },
    "tags": {
        "source": "json",
        "type": "tag",
    },
    # all language fields and conference_info.country already
    # validated in the rules with pycountry
}


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
            "value": self.metadata_provider.lower(),
        }

    def _before_create(self):
        """Perform before create metadata modification."""
        document = deepcopy(self.json_data)
        for field in self.helper_metadata_fields:
            if field in document:
                del document[field]
        # save the import source
        self._set_record_import_source(document)

        vocabulary_validator.validate(VOCABULARIES_FIELDS, document)

        return document

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
                created_date = cleaned_json.get("_created")
                if created_date:
                    document.model.created = parser.parse(created_date)
            db.session.commit()
            return document
        except IlsValidationError as e:
            click.secho("Field: {}".format(e.errors[0].res["field"]), fg="red")
            click.secho(e.original_exception.message, fg="red")
            db.session.rollback()
            raise e

    def _update_field_identifiers(self, matched_document):
        """Update isbns of a given document."""
        existing_identifiers = matched_document.get("identifiers", [])
        new_identifiers = [
            elem
            for elem in self.json_data.get("identifiers", [])
            if elem not in existing_identifiers
        ]

        return existing_identifiers + new_identifiers

    def _update_field_alternative_identifiers(self, matched_document):
        """Update alternative identifiers of a given document."""
        existing_identifiers = matched_document.get("alternative_identifiers", [])
        new_identifiers = [
            elem
            for elem in self.json_data.get("alternative_identifiers", [])
            if elem not in existing_identifiers
        ]

        return existing_identifiers + new_identifiers

    @staticmethod
    def _normalize_title(title):
        """Return a normalized title."""
        t = " ".join((title or "").lower().split())
        return t.strip()

    def update_document(self, matched_document):
        """Update document record."""
        for field in self.update_document_fields:
            if not self.json_data.get(field):
                continue
            update_field_method = getattr(self, "_update_field_{}".format(field), None)
            if update_field_method:
                matched_document[field] = update_field_method(matched_document)
            else:
                matched_document[field] = self.json_data[field]

        try:
            created_date = self.json_data.get("_created")
            if created_date:
                matched_document.model.created = parser.parse(created_date)
            matched_document.commit()
            db.session.commit()
        except IlsValidationError as e:
            click.secho("Field: {}".format(e.errors[0].res["field"]), fg="red")
            click.secho(e.original_exception.message, fg="red")
            db.session.rollback()

    def _validate_provider_identifiers(self, existing_document):
        """Validate identifiers between matches."""
        current_provider = self.metadata_provider.upper()

        import_doc_provider_ids = self.json_data.get("alternative_identifiers", [])

        doc_alternative_ids = existing_document.get("alternative_identifiers", [])

        import_provider_ids = [
            entry
            for entry in import_doc_provider_ids
            if entry.get("scheme") == current_provider
        ]

        doc_provider_ids = [
            entry
            for entry in doc_alternative_ids
            if entry.get("scheme") == current_provider
        ]

        both_have_current_provider_ids = doc_provider_ids and import_provider_ids

        matching_provider_ids = [
            entry for entry in import_doc_provider_ids if entry in doc_alternative_ids
        ]
        if both_have_current_provider_ids and not matching_provider_ids:
            # found provider ID match
            return False

        # no match found - will create a new document
        return True

    def _validate_volumes(self, existing_document):
        """Validate serial volumes match."""
        import_doc_serials = self.json_data.get("_serial", [])
        existing_doc_serials = existing_document.relations.get("serial", [])

        if not (import_doc_serials or existing_doc_serials):
            return True

        for import_serial in import_doc_serials:
            import_volume = import_serial.get("volume")
            import_serial_title = self._normalize_title(import_serial["title"])

            for serial in existing_doc_serials:
                existing_volume = serial.get("volume")
                existing_title = self._normalize_title(
                    serial["record_metadata"]["title"]
                )

                same_serial = existing_title == import_serial_title
                both_have_volumes = import_volume and existing_volume
                same_volume = existing_volume == import_volume

                if same_serial and both_have_volumes and not same_volume:
                    return False

        return True

    def _matching_isbn(self, existing_document):
        """Find matching isbns for importing document."""
        import_doc_identifiers = self.json_data.get("identifiers", [])
        import_isbns = [
            entry["value"]
            for entry in import_doc_identifiers
            if entry.get("scheme") == "ISBN"
        ]
        existing_doc_identifiers = existing_document.get("identifiers", [])
        existing_isbns = [
            entry["value"]
            for entry in existing_doc_identifiers
            if entry.get("scheme") == "ISBN"
        ]

        matching_isbns = [isbn for isbn in import_isbns if isbn in existing_isbns]
        return matching_isbns

    def validate_found_matches(self, not_validated_matches):
        """Validate matched & parsed documents have same title/isbn pair."""
        matches = []
        partial_matches = []
        match = None

        document_class = current_app_ils.document_record_cls
        import_doc_title = self.json_data.get("title")
        import_doc_edition = self.json_data.get("edition")
        import_doc_publication_year = self.json_data.get("publication_year")

        for pid_value in not_validated_matches:
            document = document_class.get_record_by_pid(pid_value)
            document_title = document["title"]
            document_edition = document.get("edition")
            doc_pub_year = document.get("publication_year")

            if self._matching_isbn(document):
                matches.append(pid_value)
            else:
                both_editions = document_edition and import_doc_edition
                editions_not_equal = (
                    both_editions and document_edition != import_doc_edition
                )

                pub_year_not_equal = doc_pub_year != import_doc_publication_year
                titles_not_equal = self._normalize_title(
                    document_title
                ) != self._normalize_title(import_doc_title)

                provider_identifiers_not_equal = (
                    not self._validate_provider_identifiers(document)
                )
                invalid_serial_volumes = not self._validate_volumes(document)

                if any(
                    [
                        titles_not_equal,
                        editions_not_equal,
                        pub_year_not_equal,
                        provider_identifiers_not_equal,
                        invalid_serial_volumes,
                    ]
                ):
                    partial_matches.append(pid_value)
                else:
                    matches.append(pid_value)

        if matches:
            match = matches[0]
        if len(matches) > 1:
            match = matches[0]
            partial_matches += matches[1:]

        return match, partial_matches

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

        title = self.json_data.get("title", None)

        if title:
            # check by title and authors, exact matching
            authors = [
                author["full_name"] for author in self.json_data.get("authors", [])
            ]
            subtitle = None
            subtitle_obj = [
                alt_title
                for alt_title in self.json_data.get("alternative_titles", [])
                if alt_title["type"] == "SUBTITLE"
            ]
            if subtitle_obj:
                subtitle = subtitle_obj[0]["value"]

            search = search_document_by_title_authors(title, authors, subtitle=subtitle)
            results = search.scan()
            matches += [x.pid for x in results if x.pid not in matches]

        return matches

    def fuzzy_match_documents(self):
        """Fuzzy search documents."""
        is_part_of_serial = self.json_data.get("_serial", None)
        title = self.json_data.get("title", None)

        if is_part_of_serial or not title:
            return []
        authors = [author["full_name"] for author in self.json_data.get("authors", [])]
        try:
            fuzzy_results = fuzzy_search_document(title, authors).scan()
        except search.TransportError:
            raise SimilarityMatchUnavailable
        return fuzzy_results

    def preview_document_import(self):
        """Preview document import JSON."""
        document_cls = current_app_ils.document_record_cls
        doc = document_cls(self._before_create())
        doc["pid"] = "preview"
        doc["$schema"] = current_jsonschemas.path_to_url(document_cls._schema)
        doc.validate()
        return doc

    def preview_document_update(self, matched_document):
        """Preview document update JSON."""
        for field in self.update_document_fields:
            if not self.json_data.get(field):
                continue
            update_field_method = getattr(self, "_update_field_{}".format(field), None)
            if update_field_method:
                matched_document[field] = update_field_method(matched_document)
            else:
                matched_document[field] = self.json_data[field]
        return matched_document
