# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Importer serializers."""

from invenio_app_ils.documents.loaders import DocumentSchemaV1
from invenio_app_ils.eitems.loaders import EItemSchemaV1
from invenio_app_ils.series.loaders import SeriesSchemaV1
from marshmallow import EXCLUDE, Schema, fields, post_dump, types

from cds_ils.importer.models import ImportRecordLog


class ImportedEItemSchema(Schema):
    """Imported EItem Schema."""

    output_pid = fields.String(dump_only=True)
    action = fields.String(dump_only=True)
    priority_provider = fields.Bool()
    duplicates = fields.List(fields.String)
    deleted_eitems = fields.List(fields.Dict)
    eitem = fields.Nested(EItemSchemaV1)
    json = fields.Raw()

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE


class ImportedSeriesSchema(Schema):
    """Imported series schema."""

    pid = fields.String(dump_only=True)
    series_json = fields.Raw()
    series_record = fields.Nested(SeriesSchemaV1)
    action = fields.String()
    output_pid = fields.String()
    duplicates = fields.List(fields.String)

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE


class PartialMatchesSchema(Schema):
    """Partial matches schema."""

    pid = fields.String(dump_only=True)
    type = fields.String()

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE


class ImporterRecordReportSchemaV1(Schema):
    """Schema for an importer task log."""

    entry_recid = fields.String()
    output_pid = fields.String()
    action = fields.String()
    document = fields.Nested(DocumentSchemaV1)
    eitem = fields.Nested(ImportedEItemSchema)
    series = fields.List(fields.Nested(ImportedSeriesSchema))
    partial_matches = fields.List(fields.Nested(PartialMatchesSchema))
    raw_json = fields.Raw()
    document_json = fields.Raw()
    success = fields.Bool(default=True)
    error = fields.Str(required=False)

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE

    @post_dump
    def status(self, data, **kwargs):
        """Return correct status."""
        error = data.get("error")
        if error:
            data["success"] = False
        return data


class ImporterTaskLogV1(Schema):
    """Importer task log schema."""

    id = fields.Integer()
    status = fields.String(dump_only=True)
    start_time = fields.DateTime(dump_only=True)
    end_time = fields.DateTime(dump_only=True)
    original_filename = fields.String(dump_only=True)
    provider = fields.String(dump_only=True)
    mode = fields.String(dump_only=True)
    source_type = fields.String(dump_only=True)
    entries_count = fields.Number(dump_only=True)

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE


class ImporterTaskDetailLogV1(ImporterTaskLogV1):
    """Importer task detail log schema."""

    def __init__(self, record_offset, **kwargs):
        """Constructor."""
        self.records_offset = record_offset
        super().__init__(**kwargs)

    @post_dump
    def records_statuses(self, data, **kwargs):
        """Return correct record statuses."""
        children_entries_query = ImportRecordLog.query.filter_by(
            import_id=data.get("id")
        ).order_by(ImportRecordLog.id.asc())

        first_entry = children_entries_query.first()

        initial_id = 0

        if first_entry:
            initial_id = first_entry.id

        entries = (
            children_entries_query.filter(
                ImportRecordLog.id >= initial_id + self.records_offset
            )
            .order_by(ImportRecordLog.id.asc())
            .all()
        )

        data["loaded_entries"] = children_entries_query.count()
        data["records"] = ImporterRecordReportSchemaV1(many=True).dump(entries)

        return data
