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


def dynamic_delete_field(original_element, fields):
    """Dynamically delete an array of fields from a dictionary."""
    # Wrong parameter in the configuration
    wrong_field = False

    for field in fields:
        if not isinstance(field, list):
            original_element.pop(field)
            continue
        if not field:
            continue

        element = original_element
        for subfield in field[:-1]:
            if subfield in element.keys():
                element = element[subfield]
            else:
                wrong_field = True
                break

        if wrong_field:
            wrong_field = False
            continue

        element.pop(field[-1], None)

    return original_element
