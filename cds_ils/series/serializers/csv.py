# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Series CSV serializers."""

from invenio_records_rest.serializers.csv import CSVSerializer

from cds_ils.utils import format_login_required_urls


class SeriesCSVSerializer(CSVSerializer):
    """Serialize Series."""

    def transform_record(self, pid, record, links_factory=None, **kwargs):
        """Transform record into an intermediate representation."""
        series = super().transform_record(
            pid, record, links_factory=links_factory, **kwargs
        )
        format_login_required_urls(series["metadata"].get("access_urls", []))
        return series

    def transform_search_hit(self, pid, record_hit, links_factory=None, **kwargs):
        """Transform search result hit into an intermediate representation."""
        hit = super().transform_search_hit(
            pid, record_hit, links_factory=links_factory, **kwargs
        )
        format_login_required_urls(hit["metadata"].get("access_urls", []))
        return hit
