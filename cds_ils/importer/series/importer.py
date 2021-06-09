# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Series Importer."""

import uuid
from copy import deepcopy

import click
from invenio_app_ils.errors import IlsValidationError, RecordRelationsError
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.records_relations.api import RecordRelationsParentChild
from invenio_app_ils.relations.api import Relation
from invenio_app_ils.series.api import SeriesIdProvider
from invenio_db import db

from cds_ils.importer.errors import SeriesImportError
from cds_ils.importer.series.api import search_series_by_isbn, \
    search_series_by_issn, search_series_by_title
from cds_ils.importer.vocabularies_validator import \
    validator as vocabulary_validator

VOCABULARIES_FIELDS = {
    "access_urls": {
        "access_restriction": {
            "source": "json",
            "type": "series_url_access_restriction",
        },
    },
    "alternative_titles": {
        "type": {
            "source": "json",
            "type": "alternative_title_type",
        },
    },
    "identifiers": {
        "scheme": {
            "source": "json",
            "type": "series_identifier_scheme",
        },
        "material": {
            "source": "json",
            "type": "doc_identifiers_materials",
        },
    },
    "tags": {
        "source": "json",
        "type": "tag",
    },
    # all language fields already validated in the rules with pycountry
}


class SeriesImporter(object):
    """Series importer class."""

    def __init__(
        self,
        json_metadata,
        metadata_provider,
    ):
        """Constructor."""
        self.json_data = json_metadata
        self.metadata_provider = metadata_provider

    def _set_record_import_source(self, record_dict):
        """Set the import source for document."""
        record_dict["created_by"] = {
            "type": "import",
            "value": self.metadata_provider,
        }

    def _before_create(self, json_series):
        """Perform before create metadata modification."""
        series = deepcopy(json_series)

        if "volume" in series:
            del series["volume"]
        # save the import source
        self._set_record_import_source(series)
        series["mode_of_issuance"] = "SERIAL"

        vocabulary_validator.validate(VOCABULARIES_FIELDS, series)

        return series

    def _update_field_identifiers(self, matched_series, json_series):
        """Update identifiers of a given series."""
        existing_identifiers = matched_series.get("identifiers", [])
        new_identifiers = [
            elem
            for elem in json_series.get("identifiers", [])
            if elem not in existing_identifiers
        ]

        return existing_identifiers + new_identifiers

    def update_series(self, matched_series, json_series):
        """Update series record."""
        matched_series["identifiers"] = self._update_field_identifiers(
            matched_series, json_series
        )
        try:
            matched_series.commit()
            db.session.commit()
        except IlsValidationError as e:
            click.secho("Field: {}".format(e.errors[0].res["field"]), fg="red")
            click.secho(e.original_exception.message, fg="red")
            db.session.rollback()
            # raise e TODO handle the incorrect records in the logging

    def create_series(self, json_series):
        """Create series record."""
        cleaned_json = self._before_create(json_series)
        series_class = current_app_ils.series_record_cls

        record_uuid = uuid.uuid4()
        provider = SeriesIdProvider.create(
            object_type="rec",
            object_uuid=record_uuid,
        )
        cleaned_json["pid"] = provider.pid.pid_value

        try:
            series = series_class.create(cleaned_json, record_uuid)
            db.session.commit()
            return series
        except IlsValidationError as e:
            click.secho("Field: {}".format(e.errors[0].res["field"]), fg="red")
            click.secho(e.original_exception.message, fg="red")
            db.session.rollback()
            # raise e TODO handle the incorrect records in the logging

    def search_for_matching_series(self, json_series):
        """Find matching series."""
        issn_list = [
            identifier["value"]
            for identifier in json_series.get("identifiers", [])
            if identifier["scheme"] == "ISSN"
        ]

        isbn_list = [
            identifier["value"]
            for identifier in json_series.get("identifiers", [])
            if identifier["scheme"] == "ISBN"
        ]

        title = json_series.get("title", None)

        matches = []
        # check by issn first

        for issn in issn_list:
            search = search_series_by_issn(issn)
            results = search.scan()
            matches += [x.pid for x in results if x.pid not in matches]

        for isbn in isbn_list:
            search = search_series_by_isbn(isbn)
            results = search.scan()
            matches += [x.pid for x in results if x.pid not in matches]

        if title:
            search = search_series_by_title(title)
            matches += [
                x.pid
                for x in search.scan()
                if x.pid not in matches and x.title == title
            ]

        return matches

    def import_serial_relation(
        self, series_record, document_record, json_series
    ):
        """Create serial relation type."""
        try:
            rr = RecordRelationsParentChild()
            serial_relation = Relation.get_relation_by_name("serial")
            volume = json_series.get("volume", None)
            rr.add(
                series_record,
                document_record,
                relation_type=serial_relation,
                volume=volume,
            )
        except RecordRelationsError as e:
            click.secho(str(e), fg="red")

    def _record_summary(self, json,
                        series_record, output_pid, action,
                        matching_series_pid_list=None):
        return {
            "series_json": self._before_create(json),
            "series_record": series_record,
            "action": action,
            "output_pid": output_pid,
            "duplicates": matching_series_pid_list
        }

    def import_series(self, document):
        """Import series."""
        series_class = current_app_ils.series_record_cls
        if self.json_data is None:
            return []

        series = []
        for json_series in self.json_data:
            matching_series_pids = self.search_for_matching_series(json_series)

            if len(matching_series_pids) == 1:
                matching_series = series_class.get_record_by_pid(
                    matching_series_pids[0]
                )
                self.update_series(matching_series, json_series)
                self.import_serial_relation(
                    matching_series, document, json_series
                )
                series.append(
                    self._record_summary(json_series,
                                         matching_series,
                                         matching_series_pids[0],
                                         action="update"
                                         ))

            elif len(matching_series_pids) == 0:
                series_record = self.create_series(json_series)
                self.import_serial_relation(
                    series_record, document, json_series
                )
                series.append(
                    self._record_summary(json_series,
                                         series_record=series_record,
                                         output_pid=None, action="create"))
            else:
                raise SeriesImportError(message="Multiple series found.")
        return series

    def preview_series(self):
        """Preview of series import."""
        series_class = current_app_ils.series_record_cls
        series_preview = []
        if self.json_data is None:
            return []

        for json_series in self.json_data:
            matching_series_pids = self.search_for_matching_series(json_series)
            if len(matching_series_pids) == 1:
                matched_series = series_class.get_record_by_pid(
                    matching_series_pids[0]
                )
                matched_series["identifiers"] = self._update_field_identifiers(
                    matched_series, json_series
                )
                series_preview.append(
                    self._record_summary(json_series,
                                         matched_series,
                                         matching_series_pids[0],
                                         action="update"
                                         ))
            elif len(matching_series_pids) == 0:
                json_series = self._before_create(json_series)
                series_preview.append(
                    self._record_summary(json_series, series_record=None,
                                         output_pid=None, action="create"))
            else:
                series_preview.append(
                    self._record_summary(
                        json_series, series_record=None,
                        output_pid=None, action="create",
                        matching_series_pid_list=matching_series_pids)
                )
        return series_preview
