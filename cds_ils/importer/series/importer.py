# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Series Importer."""

import re
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
from cds_ils.importer.providers.utils import rreplace
from cds_ils.importer.series.api import (
    search_series_by_isbn,
    search_series_by_issn,
    search_series_by_title,
)
from cds_ils.importer.vocabularies_validator import validator as vocabulary_validator

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

IGNORE_SUFFIXES = [" series", " ser", " Series", " Ser"]


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
            "value": self.metadata_provider.lower(),
        }

    def _before_create(self, json_series):
        """Perform before create metadata modification."""
        series = deepcopy(json_series)
        # Remove `Series` or `Ser` from the end while preserving the capitalization
        for substring in IGNORE_SUFFIXES:
            if re.search(substring + "$", series["title"]):
                series["title"] = rreplace(series["title"], substring, "")

        if "volume" in series:
            del series["volume"]
        # save the import source
        self._set_record_import_source(series)
        series["mode_of_issuance"] = "SERIAL"
        series["series_type"] = "SERIAL"

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

    @staticmethod
    def _normalize_title(title):
        """Return a normalized title."""
        t = " ".join((title or "").lower().split())
        # remove `series` or `ser` at the end of the title
        # `International Series of Numerical Mathematics series`
        # or `International   series of Numerical mathematics   ser`
        # will become
        # `international series of numerical mathematics`
        for substring in IGNORE_SUFFIXES:
            if re.search(substring + "$", t):
                t = rreplace(t, substring, "")
        return t.strip()

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
            raise e

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
            raise e

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

        matches = set()
        # search matching series by ISSN
        for issn in issn_list:
            search = search_series_by_issn(issn)
            matches.update({x.pid for x in search.scan()})
        # search matching series by ISBN
        for isbn in isbn_list:
            search = search_series_by_isbn(isbn)
            matches.update({x.pid for x in search.scan()})

        # search matching series by title
        title = json_series.get("title", None)
        if title:
            title = title.lower().strip()
            search = search_series_by_title(title)
            if search.count() == 0:
                # check for known inconsistencies in title
                simplified_title = self._normalize_title(title)
                search = search_series_by_title(simplified_title)

            matches.update({x.pid for x in search.scan()})

        return list(matches)

    def import_serial_relation(self, series_record, document_record, json_series):
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

    def _record_summary(
        self, json, series_record, output_pid, action, matching_series_pid_list=None
    ):
        return {
            "series_json": self._before_create(json),
            "series_record": series_record,
            "action": action,
            "output_pid": output_pid,
            "duplicates": matching_series_pid_list,
        }

    def _validate_matches(self, json_series, matches):
        """Validate matched series."""
        series_class = current_app_ils.series_record_cls
        all_series = {match: series_class.get_record_by_pid(match) for match in matches}

        def filter_non_serials(match):
            """Drops periodicals and multipart monographs."""
            _series = all_series[match]
            # Drop multipart monographs and periodicals
            is_serial = _series["mode_of_issuance"] == "SERIAL"
            is_type_serial = _series.get("series_type") == "SERIAL"
            return is_serial and is_type_serial

        matches = list(filter(filter_non_serials, matches))
        validated_matches = set()

        # matching by exact title takes precedence over anything else
        json_series_title = json_series.get("title", "").lower().strip()
        for match in matches:
            series = all_series[match]
            series_title = series["title"].lower().strip()

            is_same_title = series_title == json_series_title or self._normalize_title(
                series_title
            ) == self._normalize_title(json_series_title)
            if is_same_title:
                validated_matches.add(match)

        # if validated_matches contains matches (by title), stop here
        if validated_matches:
            return list(validated_matches)

        # Check if matching depending on the available info:
        # if ISSN exists, must match
        # if Publisher exists, must match
        # if Publication Year exists, must match

        json_series_issns = {
            id_["value"]
            for id_ in json_series.get("identifiers", [])
            if id_["scheme"] == "ISSN"
        }
        json_series_publisher = json_series.get("publisher")
        json_series_pub_year = json_series.get("publication_year")

        for match in matches:
            series = all_series[match]

            # check matching by ISSN
            series_issns = {
                id_["value"]
                for id_ in series.get("identifiers", [])
                if id_["scheme"] == "ISSN"
            }
            same_issns = json_series_issns.intersection(series_issns)
            both_have_issns = json_series_issns and series_issns
            if both_have_issns and not same_issns:
                continue

            # check matching by Publisher
            series_publisher = series.get("publisher")
            both_have_publishers = json_series_publisher and series_publisher
            if both_have_publishers:
                # if both have Publisher, it must match
                if json_series_publisher != series_publisher:
                    continue

            # check matching by Publication year
            series_pub_year = series.get("publication_year")
            both_have_pub_year = json_series_pub_year and series_pub_year
            if both_have_pub_year:
                # if both have Publication Year, it must match
                if json_series_pub_year != series_pub_year:
                    continue

            # everything matched
            validated_matches.add(match)

        return list(validated_matches)

    def import_series(self, document):
        """Import series."""
        series_class = current_app_ils.series_record_cls
        series = []
        if self.json_data is None:
            return series

        for json_series in self.json_data:
            matching_series_pids = self.search_for_matching_series(json_series)
            validated_matches = self._validate_matches(
                json_series, matching_series_pids
            )

            if len(validated_matches) == 1:
                matching_series = series_class.get_record_by_pid(validated_matches[0])
                self.update_series(matching_series, json_series)
                self.import_serial_relation(matching_series, document, json_series)
                series.append(
                    self._record_summary(
                        json_series,
                        matching_series,
                        validated_matches[0],
                        action="update",
                    )
                )

            elif len(validated_matches) == 0:
                series_record = self.create_series(json_series)
                self.import_serial_relation(series_record, document, json_series)
                series.append(
                    self._record_summary(
                        json_series,
                        series_record=series_record,
                        output_pid=series_record["pid"],
                        action="create",
                    )
                )
            else:
                series.append(
                    self._record_summary(
                        json_series,
                        series_record=None,
                        output_pid=None,
                        action="error",
                        matching_series_pid_list=matching_series_pids,
                    )
                )
                raise SeriesImportError(message="Multiple series found.")
        return series

    def preview_import_series(self):
        """Preview of series import."""
        series_class = current_app_ils.series_record_cls
        series_preview = []
        if self.json_data is None:
            return series_preview

        for json_series in self.json_data:
            matching_series_pids = self.search_for_matching_series(json_series)
            validated_matches = self._validate_matches(
                json_series, matching_series_pids
            )

            if len(validated_matches) == 1:
                matched_series = series_class.get_record_by_pid(validated_matches[0])
                matched_series["identifiers"] = self._update_field_identifiers(
                    matched_series, json_series
                )
                series_preview.append(
                    self._record_summary(
                        json_series,
                        matched_series,
                        validated_matches[0],
                        action="update",
                    )
                )
            elif len(validated_matches) == 0:
                json_series = self._before_create(json_series)
                series_preview.append(
                    self._record_summary(
                        json_series,
                        series_record=None,
                        output_pid=None,
                        action="create",
                    )
                )
            else:
                series_preview.append(
                    self._record_summary(
                        json_series,
                        series_record=None,
                        output_pid=None,
                        action="create",
                        matching_series_pid_list=validated_matches,
                    )
                )
                raise SeriesImportError(message="Multiple series found.")
        return series_preview
