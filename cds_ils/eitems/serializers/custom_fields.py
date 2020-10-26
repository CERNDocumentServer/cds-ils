# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# invenio-app-ils is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""EItem custom serializer functions."""

from flask import current_app


def format_login_required_urls(metadata):
    """Change URL endpoint when login required."""
    urls = metadata.get("urls", [])
    for url in urls:
        if url.get("login_required", False):
            url["login_required_url"] = current_app.config[
                "CDS_ILS_EZPROXY_URL"
            ].format(url=url["value"])
