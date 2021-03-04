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
from marshmallow import EXCLUDE, Schema, fields, post_dump

from cds_ils.importer.models import ImporterTaskEntry


class ImportedDocumentSchema(DocumentSchemaV1):
    """Imported document schema."""

    pid = fields.String(dump_only=True)

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE


class ImportedEItemSchema(EItemSchemaV1):
    """Imported EItem Schema."""

    pid = fields.String(dump_only=True)

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE


class ImportedSeriesSchema(SeriesSchemaV1):
    """Imported series schema."""

    pid = fields.String(dump_only=True)

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE


class ImporterRecordReportSchemaV1(Schema):
    """Schema for an importer task log."""

    entry_index = fields.Integer()
    ambiguous_documents = fields.List(fields.String)
    ambiguous_eitems = fields.List(fields.String)
    created_document = fields.Nested(ImportedDocumentSchema)
    created_eitem = fields.Nested(ImportedEItemSchema)
    updated_document = fields.Nested(ImportedDocumentSchema)
    updated_eitem = fields.Nested(ImportedEItemSchema)
    deleted_eitems = fields.List(fields.String)
    series = fields.List(fields.Nested(ImportedSeriesSchema))
    fuzzy_documents = fields.List(fields.String)

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE

    @post_dump
    def status(self, data, **kwargs):
        """Return correct status."""
        error = data.get("error")
        if error:
            data["success"] = False
            data["message"] = error
        else:
            data["success"] = True
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
        children_entries_query = ImporterTaskEntry.query \
            .filter_by(import_id=data.get('id'))
        entries = children_entries_query \
            .filter(ImporterTaskEntry.entry_index >= self.records_offset) \
            .order_by(ImporterTaskEntry.entry_index.asc()) \
            .all()
        data["loaded_entries"] = children_entries_query.count()
        data["records"] = ImporterRecordReportSchemaV1(many=True).dump(entries)
        return data
