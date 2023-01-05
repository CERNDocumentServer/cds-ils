# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""EItem JSON serializers."""

from invenio_records_rest.serializers.json import JSONSerializer

from cds_ils.utils import format_login_required_urls


class EItemJSONSerializer(JSONSerializer):
    """Serialize EItem."""

    def transform_record(self, pid, record, links_factory=None, **kwargs):
        """Transform record into an intermediate representation."""
        eitem = super().transform_record(
            pid, record, links_factory=links_factory, **kwargs
        )
        format_login_required_urls(eitem["metadata"].get("urls", []))
        return eitem

    def transform_search_hit(self, pid, record_hit, links_factory=None, **kwargs):
        """Transform search result hit into an intermediate representation."""
        hit = super().transform_search_hit(
            pid, record_hit, links_factory=links_factory, **kwargs
        )
        format_login_required_urls(hit["metadata"].get("urls", []))
        return hit
