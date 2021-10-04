# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Safari Importer module."""

from cds_ils.importer.importer import Importer


class SafariImporter(Importer):
    """OReilly importer class."""

    EITEM_OPEN_ACCESS = False
    EITEM_URLS_LOGIN_REQUIRED = False
