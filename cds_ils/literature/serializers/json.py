# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Literature JSON serializers."""

from invenio_app_ils.literature.serializers.custom_fields import field_cover_metadata
from invenio_app_ils.literature.serializers.json import (
    JSONSerializer as IlsJSONSerializer,
)

from cds_ils.utils import format_login_required_urls


class LiteratureJSONSerializer(IlsJSONSerializer):
    """Serialize Literature."""

    def transform_record(self, pid, record, links_factory=None, **kwargs):
        """Transform record into an intermediate representation."""
        literature = super().transform_record(
            pid, record, links_factory=links_factory, **kwargs
        )
        eitems = literature["metadata"].get("eitems", {}).get("hits", [])
        for eitem in eitems:
            format_login_required_urls(eitem.get("urls", []))
        field_cover_metadata(literature["metadata"])
        return literature

    def transform_search_hit(self, pid, record_hit, links_factory=None, **kwargs):
        """Transform search result hit into an intermediate representation."""
        hit = super().transform_search_hit(
            pid, record_hit, links_factory=links_factory, **kwargs
        )
        eitems = hit["metadata"].get("eitems", {}).get("hits", [])
        for eitem in eitems:
            format_login_required_urls(eitem.get("urls", []))
        field_cover_metadata(hit["metadata"])
        return hit
