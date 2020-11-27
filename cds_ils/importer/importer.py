# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer module."""
from flask import current_app
from invenio_app_ils.proxies import current_app_ils

from cds_ils.importer.documents.api import fuzzy_search_document
from cds_ils.importer.documents.importer import DocumentImporter
from cds_ils.importer.eitems.importer import EItemImporter
from cds_ils.importer.series.importer import SeriesImporter


class Importer(object):
    """Importer class."""

    UPDATE_DOCUMENT_FIELDS = ("identifiers",)
    IS_PROVIDER_PRIORITY_SENSITIVE = False
    EITEM_OPEN_ACCESS = True
    EITEM_URLS_LOGIN_REQUIRED = True

    HELPER_METADATA_FIELDS = (
        "_eitem",
        "agency_code",
        "_serial",
        "provider_recid",
    )

    def __init__(self, json_data, metadata_provider):
        """Constructor."""
        self.json_data = json_data
        self.metadata_provider = metadata_provider
        priority = current_app.config["CDS_ILS_IMPORTER_PROVIDERS"][
            metadata_provider
        ]["priority"]
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
            self.IS_PROVIDER_PRIORITY_SENSITIVE,
            self.EITEM_OPEN_ACCESS,
            self.EITEM_URLS_LOGIN_REQUIRED,
        )
        series_json = json_data.get("_serial", None)
        self.series_importer = SeriesImporter(series_json, metadata_provider)

        self.ambiguous_matches = []
        self.created = None
        self.updated = None
        self.series_list = []
        self.fuzzy_matches = []

    def _validate_provider(self):
        """Check if the chosen provider is matching the import data."""
        assert (
            self.json_data["agency_code"]
            == current_app.config["CDS_ILS_IMPORTER_PROVIDERS"][
                self.metadata_provider
            ]["agency_code"]
        )

    def _match_document(self):
        """Search the catalogue for existing document."""
        document_class = current_app_ils.document_record_cls

        matching_pids = self.document_importer.search_for_matching_documents()
        if len(matching_pids) == 1:
            return document_class.get_record_by_pid(matching_pids[0])

        self.ambiguous_matches = matching_pids

        fuzzy_results = self.document_importer.fuzzy_match_documents()
        self.fuzzy_matches = [x.pid for x in fuzzy_results]

    def import_summary(self):
        """Provide import summary."""
        return {
            "created": self.created,
            "updated": self.updated,
            "ambiguous_documents": self.ambiguous_matches,
            "fuzzy": self.fuzzy_matches,
            "series": self.series_list,
            "created_eitem": self.eitem_importer.created,
            "updated_eitem": self.eitem_importer.updated,
            "deleted_eitem_list": self.eitem_importer.deleted_list,
            "ambiguous_eitem_list": self.eitem_importer.ambiguous_list,
        }

    def update_records(self, matched_document):
        """Update document eitem and series records."""
        self.document_importer.update_document(matched_document)
        self.eitem_importer.update_eitems(matched_document)
        self.series_list = self.series_importer.import_series(matched_document)
        self.updated = matched_document

    def delete_records(self, matched_document):
        """Deletes eitems records."""
        self.eitem_importer.delete_eitems(matched_document)
        if self.eitem_importer.deleted_list:
            self.updated = matched_document

    def index_all_records(self):
        """Index imported records."""
        document_indexer = current_app_ils.document_indexer
        series_indexer = current_app_ils.series_indexer
        eitem_indexer = current_app_ils.eitem_indexer

        eitem = self.eitem_importer.updated or self.eitem_importer.created
        if eitem:
            eitem_indexer.index(eitem)
        document_indexer.index(self.created or self.updated)
        for series in self.series_list:
            series_indexer.index(series)

    def import_record(self):
        """Import record."""
        self._validate_provider()

        # finds the exact match, update records
        matched_document = self._match_document()

        if matched_document:
            self.update_records(matched_document)
            self.index_all_records()
            return self.import_summary()

        # finds the multiple matches or fuzzy matches, does not create new doc
        # requires manual intervention, to avoid duplicates
        if self.ambiguous_matches or self.fuzzy_matches:
            return self.import_summary()

        document = self.document_importer.create_document()
        if document:
            self.eitem_importer.create_eitem(document)
            self.created = document
            self.series_list = self.series_importer.import_series(document)
            self.index_all_records()
        return self.import_summary()

    def delete_record(self):
        """Deletes the eitems of the record."""
        self._validate_provider()

        # finds the exact match, update records
        matched_document = self._match_document()

        if matched_document:
            self.delete_records(matched_document)
            return self.import_summary()

        # finds the multiple matches or fuzzy matches, does not create new doc
        # requires manual intervention, to avoid duplicates
        if self.ambiguous_matches or self.fuzzy_matches:
            return self.import_summary()
        return self.import_summary()
