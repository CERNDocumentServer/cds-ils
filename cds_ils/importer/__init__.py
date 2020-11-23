# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-IlS Importer module."""

from cds_dojson.overdo import OverdoBase

# Matching to a correct model is happening here
marc21 = OverdoBase(entry_point_models="cds_ils.importer.models")
