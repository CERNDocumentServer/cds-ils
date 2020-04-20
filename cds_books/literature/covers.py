# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS Books is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Literature covers."""

from invenio_app_ils.documents.covers_builder import build_default_cover_urls


def build_literature_cover_urls(record):
    """Decorate literature with cover urls for all sizes."""

    def build_urls(url, params):
        """Build all available size urls."""
        return {
            "small": "{0}/{1}".format(url, params["small"]),
            "medium": "{0}/{1}".format(url, params["medium"]),
            "large": "{0}/{1}".format(url, params["large"]),
        }

    syndetic_client = "cernlibrary"
    syndetic_domain = "https://secure.syndetics.com/index.aspx"
    syndentic_sizes = {
        "small": "SC.gif",
        "medium": "MC.gif",
        "large": "MC.gif",
    }

    result = build_default_cover_urls(record)

    if (
        "items" in record and
        "hits" in record["items"] and
        len(record["items"]["hits"])
    ):
        cover_item = record["items"]["hits"][0]
        if "isbn" in cover_item:
            url = "{0}?client={1}&isbn={2}".format(
                syndetic_domain, syndetic_client, cover_item["isbn"]["value"])
            result = build_urls(url, syndentic_sizes)

    if "identifiers" in record:
        for identifier in record["identifiers"]:
            if identifier["scheme"] == "ISSN":
                url = "{0}?client={1}&issn={2}".format(
                    syndetic_domain, syndetic_client, identifier["value"])
                result = build_urls(url, syndentic_sizes)
                break

            if identifier["scheme"] == "ISBN":
                url = "{0}?client={1}&isbn={2}".format(
                    syndetic_domain, syndetic_client, identifier["value"])
                result = build_urls(url, syndentic_sizes)
    return result
