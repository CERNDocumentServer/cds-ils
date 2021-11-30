# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Importer serializers."""
import datetime

import math

from invenio_app_ils.documents.loaders import DocumentSchemaV1
from invenio_app_ils.eitems.loaders import EItemSchemaV1
from invenio_app_ils.series.loaders import SeriesSchemaV1
from marshmallow import EXCLUDE, Schema, fields, post_dump, types
from flask import request

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


records_cache = dict(
    id=None,
    records=[]
)


class ImporterTaskDetailLogV1(ImporterTaskLogV1):
    """Importer task detail log schema."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(**kwargs)

    @post_dump
    def records_statuses(self, data, **kwargs):
        """Return correct record statuses."""
        task_id = data.get('id')
        task_status = data.get('status')

        cached_records = records_cache['records']
        cached_records_id = records_cache['id']

        children_entries_query = ImportRecordLog.query \
            .filter_by(import_id=task_id)

        cache_empty = len(cached_records) == 0
        id_match = cached_records_id != task_id
        task_running = task_status == 'RUNNING'

        if cache_empty:
            entries = children_entries_query \
                .order_by(ImportRecordLog.id.asc()) \
                .all()
            records_cache['records'] = ImporterRecordReportSchemaV1(many=True).dump(entries)
            records_cache['id'] = task_id

        elif id_match or task_running:
            entries = children_entries_query \
                .order_by(ImportRecordLog.id.asc()) \
                .all()
            records_cache['records'] = ImporterRecordReportSchemaV1(many=True).dump(entries)
            records_cache['id'] = task_id

        serialized_records = records_cache['records']
        statistics = filter_statistics(serialized_records)

        records, page, page_size, total_pages, filter_type = paginate(statistics)

        data["loaded_entries"] = children_entries_query.count()
        data["records"] = records
        data["page"] = page
        data["page_size"] = page_size
        data['total_pages'] = total_pages
        data["filter_type"] = filter_type
        data['statistics'] = to_statistics_count(statistics)

        return data


def paginate(data):
    page = request.args.get('page') or 1
    page_size = request.args.get('page_size') or 50
    total_pages = math.ceil(len(data['all']) / int(page_size))
    filter_type = request.args.get('filter_type') or 'all'

    lower_bound_page = (int(page) * int(page_size)) - int(page_size)
    upper_bound_page = int(page_size) * int(page)

    records = data[filter_type][lower_bound_page:upper_bound_page]

    return records, page, page_size, total_pages, filter_type


def filter_statistics(data):
    create_filter_func = filter_by_attribute('create')
    update_filter_func = filter_by_attribute('update')
    delete_filter_func = filter_by_attribute('delete')
    error_filter_func = filter_by_attribute(None)

    return dict(
        all=data,
        create=filter_statistic(create_filter_func, data),
        update=filter_statistic(update_filter_func, data),
        delete=filter_statistic(delete_filter_func, data),
        error=filter_statistic(error_filter_func, data),
        eitem=filter_statistic(filter_by_eitem, data),
        serial=filter_statistic(filter_by_serials, data),
        partial=filter_statistic(filter_by_partial_matches, data)
    )


def to_statistics_count(_dict):
    dict_with_count = {}
    filter_texts = dict(
        all='RECORDS',
        create='CREATED',
        update='UPDATED',
        delete='DELETED',
        error='WITH ERRORS',
        eitem='WITH E-ITEM',
        serial='WITH SERIALS',
        partial='PARTIAL MATCHES'
    )
    for key in _dict:
        dict_with_count[key] = dict(
            value=len(_dict[key]),
            text=filter_texts[key]
        )

    return dict_with_count


def filter_by_attribute(attribute):
    return lambda record: record['action'] == attribute


def filter_by_eitem(record):
    return record['eitem'] is not None


def filter_by_serials(record):
    return record['series'] and len(record['series']) > 0


def filter_by_partial_matches(record):
    return record['partial_matches'] and len(record['partial_matches']) > 0


def filter_statistic(func, data):
    return list(filter(func, data))
