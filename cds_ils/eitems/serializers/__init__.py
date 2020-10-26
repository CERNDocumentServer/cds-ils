# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""E-items serializers."""

from invenio_app_ils.records.schemas.json import ILSRecordSchemaJSONV1
from invenio_app_ils.records.serializers import record_responsify_no_etag
from invenio_records_rest.serializers.response import search_responsify

from .csv import EItemCSVSerializer
from .json import EItemJSONSerializer

csv_v1 = EItemCSVSerializer(ILSRecordSchemaJSONV1)
csv_v1_response = record_responsify_no_etag(csv_v1, "text/csv")
csv_v1_search = search_responsify(csv_v1, "text/csv")

json_v1 = EItemJSONSerializer(ILSRecordSchemaJSONV1, replace_refs=True)
json_v1_response = record_responsify_no_etag(json_v1, "application/json")
json_v1_search = search_responsify(json_v1, "application/json")
