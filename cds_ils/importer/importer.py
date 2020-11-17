# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer module."""
import click
from invenio_app_ils.errors import RecordRelationsError
from invenio_app_ils.proxies import current_app_ils

from cds_ils.importer.config import CDS_ILS_IMPORTER_PROVIDERS
from cds_ils.importer.documents.api import fuzzy_search_document
from cds_ils.importer.documents.importer import DocumentImporter
from cds_ils.importer.eitems.importer import EItemImporter
from cds_ils.importer.series.importer import SeriesImporter


class Importer(object):
    """Importer class."""

    UPDATE_DOCUMENT_FIELDS = ("identifiers",)
    EITEMS_DELETE_LOWER_PRIORITY_PROVIDERS = False
    EITEM_OPEN_ACCESS = True
    EITEM_URLS_LOGIN_REQUIRED = True

    HELPER_METADATA_FIELDS = ("_eitem", "agency_code", "_serial")

    def __init__(self, json_data, metadata_provider):
        """Constructor."""
        self.json_data = json_data
        self.metadata_provider = metadata_provider
        priority = CDS_ILS_IMPORTER_PROVIDERS[metadata_provider]["priority"]
        self.document_importer = DocumentImporter(
            json_data,
            self.HELPER_METADATA_FIELDS,
            metadata_provider,
            self.UPDATE_DOCUMENT_FIELDS,
        )
        self.eitem_importer = EItemImporter(
            json_data,
            metadata_provider,
            priority,
            self.EITEMS_DELETE_LOWER_PRIORITY_PROVIDERS,
            self.EITEM_OPEN_ACCESS,
            self.EITEM_URLS_LOGIN_REQUIRED,
        )
        series_json = json_data.get("_serial", None)
        self.series_importer = SeriesImporter(series_json, metadata_provider)

        self.ambiguous_matches = []
        self.created = None
        self.updated = None
        self.fuzzy_matches = []

    def _validate_provider(self):
        """Check if the chosen provider is matching the import data."""
        assert (
            self.json_data["agency_code"]
            == CDS_ILS_IMPORTER_PROVIDERS[self.metadata_provider][
                "agency_code"
            ]
        )

    def _match_document(self):
        """Search the catalogue for existing document."""
        document_class = current_app_ils.document_record_cls

        matching_pids = self.document_importer.search_for_matching_documents()
        if len(matching_pids) == 1:
            return document_class.get_record_by_pid(matching_pids[0])

        self.ambiguous_matches = matching_pids

        authors = [
            author["full_name"] for author in self.json_data.get("authors", [])
        ]

        fuzzy_results = fuzzy_search_document(
            self.json_data["title"], authors
        ).scan()

        self.fuzzy_matches = [x.pid for x in fuzzy_results]

    def import_record(self):
        """Import record."""
        document_indexer = current_app_ils.document_indexer
        self._validate_provider()
        series_list = []

        # finds the exact match, update records
        matched_document = self._match_document()

        if matched_document:
            self.document_importer.update_document(matched_document)
            self.eitem_importer.update_eitems(matched_document)
            series_list = self.series_importer.import_series(matched_document)

            document_indexer.index(matched_document)

            self.updated = matched_document
            return {
                "created": None,
                "updated": self.updated["pid"],
                "ambiguous": self.ambiguous_matches,
                "fuzzy": self.fuzzy_matches,
                "series": [series["pid"] for series in series_list],
            }

        # finds the multiple matches or fuzzy matches, does not create new doc
        # requires manual intervention, to avoid duplicates
        if self.ambiguous_matches or self.fuzzy_matches:
            return {
                "created": None,
                "updated": None,
                "ambiguous": self.ambiguous_matches,
                "fuzzy": self.fuzzy_matches,
                "series": None,
            }

        document = self.document_importer.create_document()
        if document:
            self.eitem_importer.import_eitem(document)
            self.created = document
            series_list = self.series_importer.import_series(document)
            document_indexer.index(document)

            return {
                "created": self.created["pid"],
                "updated": None,
                "ambiguous": self.ambiguous_matches,
                "fuzzy": self.fuzzy_matches,
                "series": [series["pid"] for series in series_list],
            }
