# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS EItem Importer module."""

import uuid

import click
from invenio_app_ils.eitems.api import EItemIdProvider
from invenio_app_ils.errors import IlsValidationError
from invenio_app_ils.proxies import current_app_ils
from invenio_db import db

from cds_ils.importer.config import CDS_ILS_IMPORTER_PROVIDERS
from cds_ils.importer.eitems.api import get_eitems_for_document_by_provider


class EItemImporter(object):
    """EItem importer class."""

    def __init__(
        self,
        json_metadata,
        metadata_provider,
        current_provider_priority,
        delete_lower_priority_providers,
        open_access,
        login_required,
    ):
        """Constructor."""
        self.json_data = json_metadata
        self.metadata_provider = metadata_provider
        self.current_provider_priority = current_provider_priority
        self.delete_lower_priority_providers = delete_lower_priority_providers
        self.open_access = open_access
        self.login_required = login_required

    def _get_record_import_provider(self, record):
        """Get provider of the record."""
        """Get an import provider of a given document."""
        is_imported = record["created_by"]["type"] == "import"
        if is_imported:
            return record["created_by"]["value"]

    def _set_record_import_source(self, record_dict):
        """Set the provider of the record."""
        record_dict["created_by"] = {
            "type": "import",
            "value": self.metadata_provider,
        }

    def _should_overwrite_eitem(self, eitem):
        """Decide if the eitem should be replaced."""
        existing_provider = self._get_record_import_provider(eitem)

        if not existing_provider:
            return False

        existing_priority = CDS_ILS_IMPORTER_PROVIDERS[existing_provider][
            "priority"
        ]

        # existing_priority = 0, self.priority = 1, returns False
        return existing_priority >= self.current_provider_priority

    def update_eitems(self, matched_document):
        """Update eitems for given document."""
        eitem_cls = current_app_ils.eitem_record_cls
        eitem_indexer = current_app_ils.eitem_indexer
        eitem_search = current_app_ils.eitem_search_cls()

        document_pid = matched_document["pid"]

        results = get_eitems_for_document_by_provider(
            document_pid, self.metadata_provider
        )
        hits_total = results.hits.total.value
        if hits_total == 0:
            self.import_eitem(matched_document)
        elif hits_total == 1:
            try:
                existing_eitem = eitem_cls.get_record_by_pid(
                    results.hits[0].pid)
                metadata_to_update = {}
                self._build_eitem_dict(metadata_to_update,
                                       matched_document["pid"])
                existing_eitem.update(metadata_to_update)
                existing_eitem.commit()
                eitem_indexer.index(existing_eitem)
            except IlsValidationError as e:
                db.session.rollback()
                click.secho("Field: {}".format(e.errors[0].res["field"]),
                            fg="red")
                click.secho(e.original_exception.message, fg="red")
        else:
            for hit in results:
                existing_eitem = eitem_cls.get_record_by_pid(hit.pid)
                existing_eitem.delete()
            self.import_eitem(matched_document)

        if self.delete_lower_priority_providers:
            document_eitems = eitem_search.search_by_document_pid(
                matched_document["pid"]
            )
            for hit in document_eitems:
                eitem = eitem_cls.get_record_by_pid(hit.pid)
                if self._should_overwrite_eitem(eitem):
                    eitem.delete()
                    eitem_indexer.delete(eitem)

        db.session.commit()

    def _build_eitem_dict(self, eitem_json, document_pid):
        """Provide initial metadata dictionary."""
        self._apply_url_login(eitem_json)
        self._set_record_import_source(eitem_json)
        dois = [
            doi
            for doi in self.json_data.get("identifiers", [])
            if doi["scheme"] == "DOI"
        ]
        eitem_json.update(
            {
                "document_pid": document_pid,
                "open_access": self.open_access,
                "identifiers": dois,
                "created_by": {
                    "type": "import",
                    "value": self.metadata_provider,
                },
                "urls": self.json_data["_eitem"]["urls"],
                "description": self.json_data["_eitem"]["description"],
            }
        )

    def _apply_url_login(self, eitem):
        for url in eitem.get("urls", []):
            url["login_required"] = self.login_required

    def import_eitem(self, new_document):
        """Update eitems for given document."""
        eitem_cls = current_app_ils.eitem_record_cls
        eitem_json = self.json_data.get("_eitem", None)

        if eitem_json:
            try:
                self._build_eitem_dict(eitem_json, new_document["pid"])
                record_uuid = uuid.uuid4()
                provider = EItemIdProvider.create(
                    object_type="rec",
                    object_uuid=record_uuid,
                )

                eitem_json["pid"] = provider.pid.pid_value
                eitem = eitem_cls.create(eitem_json, record_uuid)
                db.session.commit()
                eitem_indexer = current_app_ils.eitem_indexer
                eitem_indexer.index(eitem)
                return eitem
            except IlsValidationError as e:
                click.secho("Field: {}".format(e.errors[0].res["field"]),
                            fg="red")
                click.secho(e.original_exception.message, fg="red")
                db.session.rollback()
                raise e
