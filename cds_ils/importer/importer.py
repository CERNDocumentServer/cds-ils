# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2025 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer module."""
import time

import importlib_metadata
from flask import current_app
from invenio_app_ils.errors import RecordHasReferencesError
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.records_relations.api import RecordRelationsParentChild
from invenio_app_ils.relations.api import Relation
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier
from invenio_search import current_search
from invenio_search.engine import search

from cds_ils.importer.documents.importer import DocumentImporter
from cds_ils.importer.eitems.importer import EItemImporter
from cds_ils.importer.errors import (
    InvalidProvider,
    SimilarityMatchUnavailable,
    UnknownProvider,
)
from cds_ils.importer.series.importer import SeriesImporter

from .errors import DocumentHasReferencesError


class Importer(object):
    """Importer class."""

    UPDATE_DOCUMENT_FIELDS = ("identifiers", "alternative_identifiers")
    IS_PROVIDER_PRIORITY_SENSITIVE = False
    EITEM_OPEN_ACCESS = True
    EITEM_URLS_LOGIN_REQUIRED = True

    HELPER_METADATA_FIELDS = (
        "_eitem",
        "agency_code",
        "_serial",
        "provider_recid",
        "_migration",
    )

    def __init__(self, json_data, metadata_provider):
        """Constructor."""
        self.json_data = json_data
        self.metadata_provider = metadata_provider

        eitem_json_data = self._extract_eitems_json()
        document_importer_class = self.get_document_importer(metadata_provider)
        self.document_importer = document_importer_class(
            json_data,
            self.HELPER_METADATA_FIELDS,
            metadata_provider,
            self.UPDATE_DOCUMENT_FIELDS,
        )
        self.eitem_importer = EItemImporter(
            json_data,
            eitem_json_data,
            metadata_provider,
            self.IS_PROVIDER_PRIORITY_SENSITIVE,
            self.EITEM_OPEN_ACCESS,
            self.EITEM_URLS_LOGIN_REQUIRED,
        )
        series_json = json_data.get("_serial", None)
        self.series_importer = SeriesImporter(series_json, metadata_provider)

    def get_document_importer(self, provider, default=DocumentImporter):
        """Determine which document importer to use."""
        try:
            entry_points = importlib_metadata.entry_points()
            return entry_points.select(group="cds_ils.document_importers")[
                provider
            ].load()
        except Exception as e:
            return default

    def _validate_provider(self):
        """Check if the chosen provider is matching the import data."""
        agency_code = self.json_data.get("agency_code")
        if not agency_code:
            raise UnknownProvider
        providers = current_app.config["CDS_ILS_IMPORTER_PROVIDERS"]
        config_agency_code = providers.get(self.metadata_provider, {}).get(
            "agency_code"
        )
        if agency_code != config_agency_code:
            raise InvalidProvider

    def _extract_eitems_json(self):
        """Extracts eitems json for given pre-processed JSON."""
        return self.json_data["_eitem"]

    def _match_document(self):
        """Search the catalogue for existing document."""
        document_importer = self.document_importer

        not_validated_matches = document_importer.search_for_matching_documents()

        exact_match, partial_matching_pids = document_importer.validate_found_matches(
            not_validated_matches
        )

        return exact_match, partial_matching_pids

    def delete_eitem(self, matched_document):
        """Deletes eitems records."""
        self.eitem_importer.delete_eitems(matched_document)
        return self.eitem_importer.summary()

    def index_records(self, document, eitem, series_list):
        """Index imported records."""
        # we are using general indexer instead of type dedicated classes
        # in order to avoid version mismatch on references
        record_indexer = RecordIndexer()

        document_class = current_app_ils.document_record_cls
        series_class = current_app_ils.series_record_cls
        eitem_class = current_app_ils.eitem_record_cls

        if eitem["output_pid"]:
            eitem = eitem_class.get_record_by_pid(eitem["output_pid"])
            record_indexer.index(eitem)
            # wait for ES refresh
            current_search.flush_and_refresh(index="eitems")

        document = document_class.get_record_by_pid(document["pid"])
        record_indexer.index(document)
        # wait for ES refresh
        current_search.flush_and_refresh(index="documents")

        for series in series_list:
            series_record = series_class.get_record_by_pid(
                series["series_record"]["pid"]
            )
            record_indexer.index(series_record)

        # wait for ES refresh
        current_search.flush_and_refresh(index="series")

    def find_partial_matches(self, pids_list=None, exact_match=None):
        """Get all partial matches."""
        if pids_list is None:
            pids_list = []
        # ambiguous = matching fails
        # (inconsistent identifiers/title pairs, duplicates etc)
        amibiguous_matches = [
            {"pid": match, "type": "ambiguous"} for match in pids_list
        ]

        # fuzzy = trying to match similar titles and authors to spot typos
        try:
            fuzzy_results = self.document_importer.fuzzy_match_documents()
            fuzzy_matches = [
                {"pid": match.pid, "type": "similar"}
                for match in fuzzy_results
                if match.pid != exact_match
            ]
        except search.TransportError:
            raise SimilarityMatchUnavailable
        return fuzzy_matches + amibiguous_matches

    def update_exact_match(self, exact_match):
        """Update exact importing record match."""
        document_class = current_app_ils.document_record_cls
        matched_document = document_class.get_record_by_pid(exact_match)

        self.document_importer.update_document(matched_document)
        self.eitem_importer.update_eitems(matched_document)

        eitem = self.eitem_importer.summary()
        series = self.series_importer.import_series(matched_document)
        return matched_document, eitem, series

    def import_record(self):
        """Import record."""
        document, eitem, series = None, None, None
        action = None
        self._validate_provider()

        exact_match, partial_matches = self._match_document()
        # finds the multiple matches or fuzzy matches, does not create new doc
        # requires manual intervention, to avoid duplicates
        partial_matches = self.find_partial_matches(partial_matches, exact_match)

        # finds the exact match, update records
        if exact_match:
            document, eitem, series = self.update_exact_match(exact_match)
            self.index_records(document, eitem, series)
            return self.report(
                document=document,
                action="update",
                partial_matches=partial_matches,
                eitem=eitem,
                series=series,
            )

        document = self.document_importer.create_document()
        if document:
            action = "create"
            self.eitem_importer.create_eitem(document)
            eitem = self.eitem_importer.summary()
            series = self.series_importer.import_series(document)
            self.index_records(document, eitem, series)

        return self.report(
            document=document,
            action=action,
            partial_matches=partial_matches,
            eitem=eitem,
            series=series,
        )

    def delete_record(self):
        """Deletes the eitems of the record."""
        document_indexer = current_app_ils.document_indexer
        series_class = current_app_ils.series_record_cls
        document_class = current_app_ils.document_record_cls

        self._validate_provider()

        exact_match, partial_matches = self._match_document()
        partial_matches = self.find_partial_matches(partial_matches, exact_match)

        if exact_match:
            matched_document = document_class.get_record_by_pid(exact_match)

            eitem = self.delete_eitem(matched_document)
            db.session.commit()
            current_search.flush_and_refresh(index="*")
            document_has_only_serial_relations = (
                len(matched_document.relations.keys())
                and "serial" in matched_document.relations.keys()
            )

            if (
                not matched_document.has_references()
                or document_has_only_serial_relations
            ):
                # remove serial relations
                rr = RecordRelationsParentChild()
                serial_relations = matched_document.relations.get("serial", [])
                relation_type = Relation.get_relation_by_name("serial")
                for relation in serial_relations:
                    serial = series_class.get_record_by_pid(relation["pid_value"])
                    rr.remove(serial, matched_document, relation_type)

            pid = matched_document.pid
            # will fail if any relations / references present
            matched_document.delete()
            # mark all PIDs as DELETED
            all_pids = PersistentIdentifier.query.filter(
                PersistentIdentifier.object_type == pid.object_type,
                PersistentIdentifier.object_uuid == pid.object_uuid,
            ).all()
            for rec_pid in all_pids:
                if not rec_pid.is_deleted():
                    rec_pid.delete()

            db.session.commit()
            document_indexer.delete(matched_document)
            return self.report(
                document=matched_document,
                action="delete",
                partial_matches=partial_matches,
                eitem=eitem,
            )

        return self.report(partial_matches=partial_matches)

    def report(
        self,
        document=None,
        action="none",
        partial_matches=None,
        eitem=None,
        series=None,
    ):
        """Generate import report."""
        doc_json = {}
        doc_pid = None
        if document:
            doc_json = document.dumps()
            doc_pid = document["pid"]
        return {
            "output_pid": doc_pid,
            "action": action,
            "partial_matches": partial_matches,
            "eitem": eitem,
            "series": series,
            "raw_json": self.json_data,
            "document_json": doc_json,
        }

    def preview_delete(self):
        """Preview deleting a record."""
        document_class = current_app_ils.document_record_cls
        document, eitem = None, None
        self._validate_provider()
        action = "none"
        # finds the exact match, update records
        exact_match, partial_matches = self._match_document()
        partial_matches = self.find_partial_matches(partial_matches, exact_match)

        if exact_match:
            document = document_class.get_record_by_pid(exact_match)
            eitem = self.eitem_importer.preview_delete(document)
            self.preview_delete_document(document)
            action = "delete"

        return self.report(
            document=document,
            action=action,
            partial_matches=partial_matches,
            eitem=eitem,
        )

    def preview_import(self):
        """Previews the record import."""
        document_class = current_app_ils.document_record_cls

        self._validate_provider()

        exact_match, partial_matches = self._match_document()
        # finds the multiple matches or fuzzy matches, does not create new doc
        # requires manual intervention, to avoid duplicates
        partial_matches = self.find_partial_matches(partial_matches, exact_match)

        if exact_match:
            document = document_class.get_record_by_pid(exact_match)
            document = self.document_importer.preview_document_update(document)
            action = "update"
        else:
            document = self.document_importer.preview_document_import()
            action = "create"

        eitem = self.eitem_importer.preview_import(document)
        series = self.series_importer.preview_import_series()

        if partial_matches:
            action = "error"

        return self.report(
            document=document,
            action=action,
            eitem=eitem,
            series=series,
            partial_matches=partial_matches,
        )

    def preview_delete_document(self, document):
        """Delete Document record."""
        loan_search_res = document.search_loan_references()
        item_search_res = document.search_item_references()
        req_search_res = document.search_doc_req_references()
        orders_refs_search = document.search_order_references()
        brw_req_refs_search = document.search_brw_req_references()

        if loan_search_res.count():
            raise DocumentHasReferencesError(
                document=document,
                ref_type="Loan",
                refs=loan_search_res,
            )

        if item_search_res.count():
            raise DocumentHasReferencesError(
                document=document,
                ref_type="Item",
                refs=item_search_res,
            )

        if req_search_res.count():
            raise DocumentHasReferencesError(
                document=document,
                ref_type="DocumentRequest",
                refs=req_search_res,
            )

        if orders_refs_search.count():
            raise DocumentHasReferencesError(
                document=document,
                ref_type="AcquisitionOrder",
                refs=orders_refs_search,
            )

        if brw_req_refs_search.count():
            raise DocumentHasReferencesError(
                document=document,
                ref_type="BorrowingRequest",
                refs=brw_req_refs_search,
            )

        related_refs = set()
        for _, related_objects in document.relations.items():
            for obj in related_objects:
                if not obj["record_metadata"].get("mode_of_issuance") == "SERIAL":
                    related_refs.add("{pid_value}:{pid_type}".format(**obj))
        if related_refs:
            raise RecordHasReferencesError(
                record_type=document.__class__.__name__,
                record_id=document["pid"],
                ref_type="related",
                ref_ids=sorted(ref for ref in related_refs),
            )
