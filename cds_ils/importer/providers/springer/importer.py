# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Springer Importer module."""

from cds_ils.importer.importer import Importer


class SpringerImporter(Importer):
    """Importer class for springer."""

    # ATTENTION: this provider has swapped order of ind1= ind2= in the XML

    IS_PROVIDER_PRIORITY_SENSITIVE = True
    EITEM_OPEN_ACCESS = False
