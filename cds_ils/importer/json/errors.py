# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-IlS JSON Importer errors module."""

from invenio_rest.errors import RESTException


class ImporterException(RESTException):
    """Importer exception."""

    code = 400

    def __init__(self, errors=None, description=None, **kwargs):
        """Constructor."""
        self.description = description
        super().__init__(errors, **kwargs)
