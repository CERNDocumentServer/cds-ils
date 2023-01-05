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
    ILSRecordSchemaJSONV1,
    csv_excluded_fields=[
        "links",
        "metadata_$schema",
        "metadata_document_cover_metadata_ISBN",
        "metadata_document_cover_metadata_isbn",
        "metadata_item_description",
        "metadata_item_document_pid",
        "metadata_item_medium",
        "metadata_item_pid_type",
        "metadata_item_pid_value",
        "metadata_item_suggestion_status",
        "metadata_patron_location_pid",
        "metadata_patron_pid",
        "metadata_pickup_location_pid",
        "metadata_pid",
        "metadata_transaction_user_pid",
        "metadata_transaction_location_pid",
        "metadata_transaction_date",
        "metadata_document_authors",
        "metadata_document_document_type",
        "metadata_document_edition",
        "metadata_document_publication_year",
        "metadata_patron_id",
        "metadata_item_suggestion_internal_location_location_name",
    ],
)
csv_v1_response = record_responsify_no_etag(csv_v1, "text/csv")
csv_v1_search = search_responsify(csv_v1, "text/csv")
