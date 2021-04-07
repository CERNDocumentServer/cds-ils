# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Utils for modules."""
from flask import current_app


def format_login_required_urls(urls):
    """Change URL endpoint when login required."""
    for url in urls:
        if url.get("login_required", False):
            url["login_required_url"] = current_app.config[
                "CDS_ILS_EZPROXY_URL"
            ].format(url=url["value"])
