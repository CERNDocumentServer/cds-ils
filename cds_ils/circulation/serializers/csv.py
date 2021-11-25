# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Literature CSV serializers."""

from flask import current_app
from invenio_app_ils.circulation.serializers.csv import \
    LoanCSVSerializer as IlsLoanCSVSerializer

from cds_ils.utils import dynamic_delete_field


class LoanCSVSerializer(IlsLoanCSVSerializer):
    """Serialize literature."""

    def transform_record(self, pid, record, links_factory=None, **kwargs):
        """Transform record into an intermediate representation."""
        loan = super().transform_record(
            pid, record, links_factory=links_factory, **kwargs
        )
        return loan

    def transform_search_hit(
        self, pid, record_hit, links_factory=None, **kwargs
    ):
        """Transform search result hit into an intermediate representation."""
        hit = super().transform_search_hit(
            pid, record_hit, links_factory=links_factory, **kwargs
        )
        return dynamic_delete_field(
            hit, current_app.config["CDS_LOAN_SERIALIZE_FIELDS_REMOVE"]
        )
