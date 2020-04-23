# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS Books is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Literature covers."""


def build_literature_cover_urls(metadata):
    """Decorate literature with cover urls for all sizes."""
    client = "cernlibrary"
    url = "https://secure.syndetics.com/index.aspx"
    cover_metadata = metadata.get("cover_metadata", {})
    isbn = cover_metadata.get("isbn", "")
    return {
        "small": "{url}?client={client}&isbn={isbn}/SC.gif".format(
            url=url, client=client, isbn=isbn),
        "medium": "{url}?client={client}&isbn={isbn}/MC.gif".format(
            url=url, client=client, isbn=isbn),
        "large": "{url}?client={client}&isbn={isbn}/LC.gif".format(
            url=url, client=client, isbn=isbn),
    }
