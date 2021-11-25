# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Loan serializers."""
from invenio_app_ils.circulation.serializers.csv import LoanCSVSerializer
from invenio_app_ils.records.schemas.json import ILSRecordSchemaJSONV1
from invenio_app_ils.records.serializers import record_responsify_no_etag
from invenio_records_rest.serializers.response import search_responsify

csv_v1 = LoanCSVSerializer(
    ILSRecordSchemaJSONV1, csv_excluded_fields=["links"]
)
csv_v1_response = record_responsify_no_etag(csv_v1, "text/csv")
csv_v1_search = search_responsify(csv_v1, "text/csv")
