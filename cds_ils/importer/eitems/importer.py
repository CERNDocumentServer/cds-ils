# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS EItem Importer module."""

import uuid

import click
from flask import current_app
from invenio_app_ils.eitems.api import EItemIdProvider
from invenio_app_ils.errors import IlsValidationError
from invenio_app_ils.proxies import current_app_ils
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier

from cds_ils.importer.eitems.api import get_eitems_for_document_by_provider


class EItemImporter(object):
    """EItem importer class."""

    def __init__(
        self,
        json_metadata,
        eitem_json_data,
        metadata_provider,
        provider_priority_sensitive,
        open_access,
        login_required,
    ):
        """Constructor."""
        priority = current_app.config["CDS_ILS_IMPORTER_PROVIDERS"][metadata_provider][
            "priority"
        ]
        self.json_data = json_metadata
        self.metadata_provider = metadata_provider
        self.current_provider_priority = priority
        self.is_provider_priority_sensitive = provider_priority_sensitive
        self.open_access = open_access
        self.login_required = login_required

        self.eitem_json = eitem_json_data
        self.output_pid = None
        self.action = None
        self.eitem_record = None
        self.ambiguous_list = []
        self.deleted_list = []

    def _is_imported(self, record):
        return record["created_by"]["type"] == "import"

    def _is_manually_created(self, record):
        return record["created_by"]["type"] == "user_id"

    def _is_migrated(self, record):
        return (
            record["created_by"]["type"] == "script"
            and record["created_by"]["value"] == "migration"
        )

    def _get_record_import_provider(self, record):
        """Get an import provider of a given document."""
        if self._is_imported(record):
            return record["created_by"]["value"].lower()
        elif self._is_manually_created(record):
            return record.get("source", "").lower()
        elif self._is_migrated(record):
            return record.get("source", "").lower()

    def _set_record_import_source(self, record_dict):
        """Set the provider of the record."""
        record_dict["created_by"] = {
            "type": "import",
            "value": self.metadata_provider.lower(),
        }
        record_dict["source"] = self.metadata_provider

    def _eitem_has_higher_priority(self, eitem, priority=None):
        """Replace the eitems with higher priority providers."""
        priority = priority or self.current_provider_priority

        PRIORITY_FOR_UNKNOWN = 100  # high number means low priority
        PROVIDERS = current_app.config["CDS_ILS_IMPORTER_PROVIDERS"]

        eitem_provider = self._get_record_import_provider(eitem)
        provider_definition = PROVIDERS.get(eitem_provider, {})
        eitem_priority = provider_definition.get("priority", PRIORITY_FOR_UNKNOWN)

        # existing_priority = 0, self.priority = 1, returns True
        # 0 is considered higher priority than 1
        return eitem_priority < priority

    def _update_existing_record(self, existing_eitem, matched_document):
        metadata_to_update = {}
        self._build_eitem_json(metadata_to_update, matched_document["pid"])
        try:
            existing_eitem.update(metadata_to_update)
            existing_eitem.commit()
            db.session.commit()
            return existing_eitem
        except IlsValidationError as e:
            db.session.rollback()
            click.secho("Field: {}".format(e.errors[0].res["field"]), fg="red")
            click.secho(e.original_exception.message, fg="red")

    def _delete_existing_record(self, existing_eitem):
        eitem_indexer = current_app_ils.eitem_indexer
        pid = existing_eitem.pid
        pid_object_type, pid_object_uuid = pid.object_type, pid.object_uuid
        existing_eitem.delete()

        # mark all PIDs as DELETED
        all_pids = PersistentIdentifier.query.filter(
            PersistentIdentifier.object_type == pid_object_type,
            PersistentIdentifier.object_uuid == pid_object_uuid,
        ).all()
        for rec_pid in all_pids:
            if not rec_pid.is_deleted():
                rec_pid.delete()
        db.session.commit()
        eitem_indexer.delete(existing_eitem)
        return existing_eitem

    def _report_ambiguous_records(self, multiple_results):
        eitem_cls = current_app_ils.eitem_record_cls

        for hit in multiple_results:
            existing_eitem = eitem_cls.get_record_by_pid(hit["pid"])
            self.ambiguous_list.append(existing_eitem)

    def _get_other_eitems_of_document(self, matched_document):
        eitem_search = current_app_ils.eitem_search_cls()
        eitem_cls = current_app_ils.eitem_record_cls

        document_eitems = eitem_search.search_by_document_pid(matched_document["pid"])
        for hit in document_eitems:
            yield eitem_cls.get_record_by_pid(hit.pid)

    def _replace_lower_priority_eitems(self, matched_document):
        eitem_indexer = current_app_ils.eitem_indexer

        for eitem in self._get_other_eitems_of_document(matched_document):
            # If eitem_type is different, then creation should happen
            if eitem["eitem_type"] != self.eitem_json.get("_type", "E-BOOK").upper():
                continue
            is_imported = self._is_imported(eitem)

            # replace conditions
            if not is_imported:
                continue

            existing_has_higher_priority = self._eitem_has_higher_priority(eitem)
            if not existing_has_higher_priority:
                self.deleted_list.append(eitem)
                pid = eitem.pid
                pid_object_type, pid_object_uuid = pid.object_type, pid.object_uuid
                eitem.delete()
                # mark all PIDs as DELETED
                all_pids = PersistentIdentifier.query.filter(
                    PersistentIdentifier.object_type == pid_object_type,
                    PersistentIdentifier.object_uuid == pid_object_uuid,
                ).all()
                for rec_pid in all_pids:
                    if not rec_pid.is_deleted():
                        rec_pid.delete()
                db.session.commit()
                eitem_indexer.delete(eitem)
        if self.deleted_list:
            self.action = "replace"

    def _should_import_eitem_by_type_priority(self, matched_document):
        """Check if current eitem has priority lower than any existing."""
        existing_eitems = self._get_other_eitems_of_document(matched_document)

        comparison_list = []
        for eitem in existing_eitems:
            # If eitem_type is different, then creation should happen regardless of priority
            if eitem["eitem_type"] != self.eitem_json.get("_type", "E-BOOK").upper():
                continue
            is_imported_or_created = (
                self._is_imported(eitem)
                or self._is_manually_created(eitem)
                or self._is_migrated(eitem)
            )
            if not is_imported_or_created:
                # skip until you find imported items to compare
                continue
            existing_has_higher_priority = self._eitem_has_higher_priority(eitem)

            comparison_list.append(existing_has_higher_priority)

        # if none of the existing e-items has higher priority
        # or none were imported
        return not any(comparison_list)

    def _build_eitem_json(self, eitem_json, document_pid, urls=None, description=None):
        """Provide initial metadata dictionary."""
        self._apply_url_login(self.eitem_json)
        self._set_record_import_source(eitem_json)
        dois = [
            doi
            for doi in self.json_data.get("identifiers", [])
            if doi["scheme"] == "DOI"
        ]
        eitem_json.update(
            dict(
                document_pid=document_pid,
                eitem_type=self.eitem_json.get("_type", "E-BOOK").upper(),
                open_access=self.open_access,
                identifiers=dois,
                urls=self.eitem_json.get("urls", []),
                description=self.eitem_json.get("description", ""),
            )
        )

    def _apply_url_login(self, eitem):
        """Update login required property of urls."""
        for url in eitem.get("urls", []):
            url["login_required"] = self.login_required

    def eitems_search(self, matched_document):
        """Search items for given document."""
        document_pid = matched_document["pid"]
        # get eitems for current provider
        search = get_eitems_for_document_by_provider(
            document_pid, self.metadata_provider
        ).filter("term", eitem_type=self.eitem_json.get("_type", "E-BOOK").upper())
        return search

    def import_eitem_action(self, search):
        """Determine import action."""
        # If found more than 0 then update for the same type & provider, if eitem with same type & provider isn't found then do create
        hits_count = search.count()
        if hits_count == 1:
            self.action = "update"
        elif hits_count == 0:
            self.action = "create"

    def get_first_match(self, search):
        """Return first matched record from search."""
        eitem_cls = current_app_ils.eitem_record_cls
        results = search.execute()
        record = results.hits[0]
        return eitem_cls.get_record_by_pid(record["pid"])

    def update_eitems(self, matched_document):
        """Update eitems for a given document."""
        search = self.eitems_search(matched_document)
        self.import_eitem_action(search)

        # determine currently imported eitem provider priority
        should_eitem_be_imported = self._should_import_eitem_by_type_priority(
            matched_document
        )

        if self.action == "create" and should_eitem_be_imported:
            self.eitem_record = self.create_eitem(matched_document)
            if self.is_provider_priority_sensitive:
                self._replace_lower_priority_eitems(matched_document)
        elif self.action == "update":
            existing_eitem = self.get_first_match(search)
            self.eitem_record = self._update_existing_record(
                existing_eitem, matched_document
            )
            self.output_pid = existing_eitem["pid"]
        else:
            results = search.scan()
            self._report_ambiguous_records(results)
            # still creates an item, even ambiguous eitems found
            # checks if there are higher priority eitems
            if should_eitem_be_imported:
                self.eitem_record = self.create_eitem(matched_document)
            else:
                self.action = "none"

    def delete_eitems(self, matched_document):
        """Deletes eitems for a given document."""
        eitem_cls = current_app_ils.eitem_record_cls
        document_pid = matched_document["pid"]
        self.action = "delete"

        # get eitems for current provider
        search = get_eitems_for_document_by_provider(
            document_pid, self.metadata_provider
        )
        results = search.scan()

        for record in results:
            existing_eitem = eitem_cls.get_record_by_pid(record["pid"])
            self.deleted_list.append(self._delete_existing_record(existing_eitem))

    def preview_delete(self, matched_document):
        """Preview delete action on eitems for given document."""
        eitem_cls = current_app_ils.eitem_record_cls
        document_pid = matched_document["pid"]
        self.action = "delete"
        search = get_eitems_for_document_by_provider(
            document_pid, self.metadata_provider
        )
        results = search.scan()
        for record in results:
            existing_eitem = eitem_cls.get_record_by_pid(record["pid"])
            self.deleted_list.append(existing_eitem)

        return self.summary()

    def create_eitem(self, new_document):
        """Update eitems for given document."""
        eitem_cls = current_app_ils.eitem_record_cls
        if self.eitem_json:
            try:
                self._build_eitem_json(self.eitem_json, new_document["pid"])
                record_uuid = uuid.uuid4()
                with db.session.begin_nested():
                    provider = EItemIdProvider.create(
                        object_type="rec",
                        object_uuid=record_uuid,
                    )

                    self.eitem_json["pid"] = provider.pid.pid_value
                    self.eitem_record = eitem_cls.create(self.eitem_json, record_uuid)
                db.session.commit()
                self.action = "create"
                self.output_pid = self.eitem_record["pid"]
                return self.eitem_record
            except IlsValidationError as e:
                click.secho("Field: {}".format(e.errors[0].res["field"]), fg="red")
                click.secho(e.original_exception.message, fg="red")
                db.session.rollback()
                raise e

    def summary(self):
        """Summarize the import."""
        return {
            "eitem": self.eitem_record,
            "json": self.eitem_json,
            "output_pid": self.output_pid,
            "duplicates": self.ambiguous_list,
            "action": self.action,
            "deleted_eitems": self.deleted_list,
        }

    def preview_import(self, matched_document):
        """Preview eitem JSON."""
        self.action = "create"
        if matched_document:
            pid = matched_document["pid"]
            search = self.eitems_search(matched_document)
            self.import_eitem_action(search)
            # determine currently imported eitem provider priority
            should_eitem_be_imported = self._should_import_eitem_by_type_priority(
                matched_document
            )

            if self.action == "update":
                self._build_eitem_json(self.eitem_json, pid)
                self.output_pid = self.get_first_match(search)["pid"]

                return self.summary()
            else:
                results = search.scan()
                self._report_ambiguous_records(results)
                # still creates an item, even ambiguous eitems found
                # checks if there are higher priority eitems
                if should_eitem_be_imported:
                    self.action = "create"
                    self.eitem_record = self.eitem_json
                else:
                    self.action = "none"

        self.output_pid = "preview-doc-pid"
        self._build_eitem_json(self.eitem_json, self.output_pid)

        if self.is_provider_priority_sensitive and self.action == "create":
            # check if any existing items will be replaced
            eitem_search = current_app_ils.eitem_search_cls()
            eitem_cls = current_app_ils.eitem_record_cls

            if matched_document:
                document_eitems = eitem_search.search_by_document_pid(
                    matched_document["pid"]
                )
                for hit in document_eitems:
                    eitem = eitem_cls.get_record_by_pid(hit.pid)
                    is_imported_or_created = (
                        self._is_imported(eitem)
                        or self._is_manually_created(eitem)
                        or self._is_migrated(eitem)
                    )
                    if not is_imported_or_created:
                        continue
                    existing_has_higher_priority = self._eitem_has_higher_priority(
                        eitem
                    )
                    if not existing_has_higher_priority:
                        self.deleted_list.append(eitem)
                if self.deleted_list:
                    self.action = "replace"

        return self.summary()
