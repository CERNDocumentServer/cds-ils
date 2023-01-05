# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Series JSON serializers."""
from invenio_app_ils.literature.serializers.custom_fields import field_cover_metadata
from invenio_records_rest.serializers.json import JSONSerializer

from cds_ils.utils import format_login_required_urls


class SeriesJSONSerializer(JSONSerializer):
    """Serialize Series."""

    def transform_record(self, pid, record, links_factory=None, **kwargs):
        """Transform record into an intermediate representation."""
        series = super().transform_record(
            pid, record, links_factory=links_factory, **kwargs
        )
        format_login_required_urls(series["metadata"].get("access_urls", []))
        field_cover_metadata(series["metadata"])
        return series

    def transform_search_hit(self, pid, record_hit, links_factory=None, **kwargs):
        """Transform search result hit into an intermediate representation."""
        hit = super().transform_search_hit(
            pid, record_hit, links_factory=links_factory, **kwargs
        )
        format_login_required_urls(hit["metadata"].get("access_urls", []))
        field_cover_metadata(hit["metadata"])
        return hit
