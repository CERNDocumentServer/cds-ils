# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Blueprint used for loading templates.

The sole purpose of this blueprint is to ensure that Invenio can find the
templates and static files located in the folders of the same names next to
this file.
"""

from flask import Blueprint

blueprint = Blueprint(
    "cds_ils_ui",
    __name__,
    template_folder="templates",
    static_folder="static",
)
