# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Gobi Importer module."""

from cds_ils.importer.importer import Importer


class GOBIImporter(Importer):
    """Importer class for GOBI."""

    EITEM_OPEN_ACCESS = False
    EITEM_URLS_LOGIN_REQUIRED = True
