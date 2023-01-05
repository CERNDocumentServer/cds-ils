# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Literature CSV serializers."""

from invenio_app_ils.literature.serializers.csv import (
    LiteratureCSVSerializer as IlsLiteratureCSVSerializer,
)

from cds_ils.utils import format_login_required_urls


class LiteratureCSVSerializer(IlsLiteratureCSVSerializer):
    """Serialize literature."""

    def transform_record(self, pid, record, links_factory=None, **kwargs):
        """Transform record into an intermediate representation."""
        literature = super().transform_record(
            pid, record, links_factory=links_factory, **kwargs
        )
        format_login_required_urls(literature["metadata"].get("urls", []))
        return literature

    def transform_search_hit(self, pid, record_hit, links_factory=None, **kwargs):
        """Transform search result hit into an intermediate representation."""
        hit = super().transform_search_hit(
            pid, record_hit, links_factory=links_factory, **kwargs
        )
        format_login_required_urls(hit["metadata"].get("urls", []))
        return hit
